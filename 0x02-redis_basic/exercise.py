#!/usr/bin/env python3
'''A module for using the Redis NoSQL data storage.
'''
import redis
import uuid
from typing import Callable, Optional, Union
import functools

# Decorator to store call history of a method (inputs and outputs)
def call_history(method: Callable) -> Callable:
    """Decorator that stores the history of inputs and outputs of a method in Redis."""

    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        input_key = method.__qualname__ + ":inputs"
        output_key = method.__qualname__ + ":outputs"
        self._redis.rpush(input_key, str(args))
        output = method(self, *args, **kwargs)
        self._redis.rpush(output_key, str(output))
        return output

    return wrapper

# Decorator to count calls to a method
def count_calls(method: Callable) -> Callable:
    """Decorator that counts the number of calls to a method using Redis."""

    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        key = method.__qualname__
        self._redis.incr(key)
        return method(self, *args, **kwargs)

    return wrapper

class Cache:
    def __init__(self):
        """Initialize the Redis client and flush the database."""
        self._redis = redis.Redis()
        self._redis.flushdb()

    @call_history
    @count_calls
    def store(self, data: Union[str, bytes, int, float]) -> str:
        """Generate a random key, store data in Redis, and return the key."""
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key

    def get(self, key: str, fn: Optional[Callable] = None) -> Union[str, bytes, int, float, None]:
        """Retrieve data from Redis by key and apply an optional conversion function."""
        data = self._redis.get(key)
        if data is None:
            return None
        if fn:
            return fn(data)
        return data

    def get_str(self, key: str) -> Optional[str]:
        """Retrieve data as a string, decoded from bytes."""
        return self.get(key, fn=lambda d: d.decode("utf-8"))

    def get_int(self, key: str) -> Optional[int]:
        """Retrieve data as an integer, decoded from bytes."""
        return self.get(key, fn=int)

    def get_call_count(self, method_name: str) -> int:
        """Get the number of times a method has been called by its qualified name."""
        return int(self._redis.get(method_name) or 0)

    def get_input_history(self, method_name: str) -> list:
        """Retrieve the input history of a method from Redis."""
        key = method_name + ":inputs"
        return self._redis.lrange(key, 0, -1)

    def get_output_history(self, method_name: str) -> list:
        """Retrieve the output history of a method from Redis."""
        key = method_name + ":outputs"
        return self._redis.lrange(key, 0, -1)

# Replay function
def replay(method: Callable) -> None:
    """Display the history of calls to a particular function."""
    # Get the fully qualified name of the method
    method_name = method.__qualname__

    # Retrieve input and output histories from Redis
    cache_instance = method.__self__
    inputs = cache_instance.get_input_history(method_name)
    outputs = cache_instance.get_output_history(method_name)

    # Get the number of times the method was called
    call_count = cache_instance.get_call_count(method_name)

    # Print the replay output
    print(f"{method_name} was called {call_count} times:")

    for input_args, output in zip(inputs, outputs):
        print(f"{method_name}(*{input_args.decode('utf-8')}) -> {output.decode('utf-8')}")

