"""
In-memory caching module

Fast
        Insert and get <= O(log n)
Powerful
        Thread safe
        Global and per key ttl
        Size limit with LRU
Simple
        Decorator with custom caching keys (TODO)
"""

import time
from threading import Lock

try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict


class CacheMissException(Exception):
    pass


class SimpleCache(object):

    CacheMissException = CacheMissException

    def __init__(self, cache_size=100000, ttl=None):
        if cache_size <= 0:
            raise AttributeError('cache_size has to be None or int > 0')

        if ttl is not None and ttl <= 0:
            raise AttributeError('ttl has to be None or float > 0')

        self._cache = OrderedDict()

        self._max_cache_size = cache_size
        self._default_ttl = float(ttl) if ttl else None

        self._lock = Lock()

    def put(self, key, val, ttl=None):
        if ttl is not None and ttl <= 0:
            raise AttributeError('ttl has to be None or float > 0')

        ttl = ttl if ttl else self._default_ttl
        expires = (float(ttl) + time.time()) if ttl else False

        with self._lock:
            try:
                del self._cache[key]
            except KeyError:
                self._remove_lru()

            self._cache[key] = (expires, val)

    def _get_unlocked(self, key):
        try:
            val = self._cache[key]
        except KeyError:
            raise self.CacheMissException

        if val[0] is not False and val[0] < time.time():
            del self._cache[key]
            raise self.CacheMissException

        del self._cache[key]
        self._cache[key] = val

        return val[1]

    def get(self, key):
        with self._lock:
            return self._get_unlocked(key)

    def multiget(self, keys):
        values = []
        with self._lock:
            for key in keys:
                try:
                    values.append(self._get_unlocked(key))
                except self.CacheMissException:
                    values.append(None)
        return values

    def _remove_lru(self):
        if len(self._cache) >= self._max_cache_size:
            self._cache.popitem(last=False)
