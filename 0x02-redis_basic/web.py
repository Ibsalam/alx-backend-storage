#!/usr/bin/env python3
'''A module with tools for request caching and tracking.
'''
import redis
import requests
from typing import Callable

# Initialize Redis client
r = redis.Redis()

def get_page(url: str) -> str:
    """Fetch the HTML content of a URL and cache it with a 10-second expiration."""

    # Create a key for the count and for the cached page
    count_key = f"count:{url}"
    cache_key = f"cached:{url}"

    # Increment the count for this URL
    r.incr(count_key)

    # Check if the result is already cached
    cached_page = r.get(cache_key)
    if cached_page:
        return cached_page.decode('utf-8')

    # If not cached, fetch the page from the URL
    response = requests.get(url)
    page_content = response.text

    # Cache the result with a 10-second expiration
    r.setex(cache_key, 10, page_content)

    return page_content

# Optional: Bonus, implementing caching with a decorator
def cache_page(method: Callable) -> Callable:
    """Decorator to cache the page result with a 10-second expiration and track accesses."""

    def wrapper(url: str) -> str:
        # Create keys for caching and counting
        count_key = f"count:{url}"
        cache_key = f"cached:{url}"

        # Increment the count for the URL
        r.incr(count_key)

        # Check if result is already cached
        cached_page = r.get(cache_key)
        if cached_page:
            return cached_page.decode('utf-8')

        # Fetch page if not cached
        page_content = method(url)

        # Cache the result with a 10-second expiration
        r.setex(cache_key, 10, page_content)

        return page_content

    return wrapper

# Applying the decorator to get_page function
@cache_page
def get_page_with_decorator(url: str) -> str:
    """Fetch the HTML content of a URL."""
    response = requests.get(url)
    return response.text

