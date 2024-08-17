#!/usr/bin/env python3
'''A module for using the Redis NoSQL data storage.
'''
import redis
import uuid
from typing import Union

class Cache:
    def __init__(self):
        """Initialize the Redis client and flush the database."""
        self._redis = redis.Redis()
        self._redis.flushdb()

    def store(self, data: Union[str, bytes, int, float]) -> str:
        """Generate a random key, store data in Redis, and return the key."""
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key

