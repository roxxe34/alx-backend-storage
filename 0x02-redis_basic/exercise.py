#!/usr/bin/env python3
"""
Writing strings to Redis
"""

import redis
import uuid
from typing import Union, Callable, Optional
from functools import wraps
import sys

UnionTypes = Union[str, bytes, int, float]


def count_calls(method: Callable) -> Callable:
    """
    a system to count how many
    times methods of the Cache class are called.
    """
    key = method.__qualname__

    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """
        Wraper
        """
        self._redis.incr(key)
        return method(self, *args, **kwargs)

    return wrapper


def call_history(method: Callable) -> Callable:
    """
    add its input parameters to a list
    in redis, and store its output into another list.
    """
    key = method.__qualname__
    i = "".join([key, ":inputs"])
    o = "".join([key, ":outputs"])

    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """ Wrapp """
        self._redis.rpush(i, str(args))
        res = method(self, *args, **kwargs)
        self._redis.rpush(o, str(res))
        return res

    return wrapper


class Cache:
    """
    A class that represents a cache using Redis.
    """
    def __init__(self):
        self._redis = redis.Redis()
        self._redis.flushdb()

    @count_calls
    @call_history
    def store(self, data: UnionTypes) -> str:
        """
        store(data: UnionTypes) -> str: Stores the given
        data in the cache and returns the generated key."""
        key = str(uuid.uuid4())
        self._redis.mset({key: data})
        return key

    def get(self, key: str, fn: Optional[Callable] = None) -> UnionTypes:
        """
        get(key: str, fn: Optional[Callable] = None) -> UnionTypes: Retrieves
        the data associated with the given key from the cache.
        """
        data = self._redis.get(key)
        if fn:
            return fn(data)
        return data

    def get_int(self: bytes) -> int:
        """get a number"""
        return int.from_bytes(self, sys.byteorder)

    def get_str(self: bytes) -> str:
        """get a string"""
        return self.decode("utf-8")
