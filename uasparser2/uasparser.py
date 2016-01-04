import os
import platform
import time

try:
    import cPickle as pickle
except ImportError:
    import pickle

try:
    from urllib2 import urlopen
except ImportError:
    from urllib.request import urlopen

from .imcache import SimpleCache
from .decorators import deprecated
from .ini_data_loader import IniDataLoader
from .matcher import UASMatcher
from .constants import INI_URL, DEFAULT_TMP_DIR, VERSION


_CACHE_FILE_NAME = 'uasparser2_{lib_version}_{python_version}_cache.pickle'


class UASException(Exception):
    pass


class UASParser(object):

    def __init__(self, cache_dir=None, mem_cache_size=1000, cache_ttl=None):
        """
        Args:
            cache_dir: String, path to the cache dir for useragent parsing data, default is /tmp.
            cache_ttl: Int, ttl for useragent parsing data cache in seconds, default is never.
                       Cache ttl is only checked on init when data is loaded.
            mem_cache_size: Int, number of parsed useragents to cache, default is 1000.
        """

        self._cache_file_name = self._get_cache_file_name(cache_dir)
        self._cache_ttl = cache_ttl

        self._mem_cache_size = mem_cache_size
        self._mem_cache = self._mem_cache_size and SimpleCache(cache_size=self._mem_cache_size)

        self._ini_data_loader = IniDataLoader()
        self._uas_matcher = None

        self._load_data()

    def _get_cache_file_name(self, cache_dir):
        cache_dir = cache_dir or DEFAULT_TMP_DIR

        if not os.access(cache_dir, os.W_OK):
            raise UASException("Cache directory %s is not writable." % cache_dir)

        return os.path.join(
            cache_dir,
            _CACHE_FILE_NAME.format(
                lib_version=VERSION,
                python_version=platform.python_version(),
            )
        )

    def parse(self, useragent):
        """
        Get the information of an useragent string
        Args:
            useragent: String, an useragent string
        """
        if not useragent:
            raise UASException("Excepted argument useragent is not given.")

        if self._mem_cache:
            try:
                return self._mem_cache.get(useragent)
            except self._mem_cache.CacheMissException:
                pass

        result = self._uas_matcher.match(useragent)

        if self._mem_cache:
            self._mem_cache.put(useragent, result)

        return result

    def _fetch_url(self, url):
        context = urlopen(url)
        return context

    def _check_cache(self):
        cache_file = self._cache_file_name
        if not os.path.exists(cache_file):
            return False

        return True

    def _load_cache(self):
        try:
            cache_data = pickle.load(open(self._cache_file_name, 'rb'))
        except Exception:
            self.update_data()
            return

        if self._cache_ttl is not None and cache_data['timestamp'] < time.time() - self._cache_ttl:
            self.update_data()
            return

        self._uas_matcher = UASMatcher(cache_data['data'])

    def update_data(self):
        """
        Fetch useragent parsing data from http://user-agent-string.info/ and update local cache
        """
        try:
            cache_file = open(self._cache_file_name, 'wb')
            ini_file = self._fetch_url(INI_URL)
            ini_data = self._ini_data_loader.parse_ini_file(ini_file)
        except:
            raise UASException("Failed to download cache data")

        self._uas_matcher = UASMatcher(ini_data)

        cache_data = {
            'data': ini_data,
            'timestamp': time.time(),
        }
        pickle.dump(cache_data, cache_file)

        if self._mem_cache:
            self._mem_cache = SimpleCache(cache_size=self._mem_cache_size)

        return True

    def _load_data(self):
        if self._check_cache():
            self._load_cache()
        else:
            self.update_data()


class UASparser(UASParser):

    @deprecated
    def __init__(self, *args, **kwargs):
        super(UASparser, self).__init__(*args, **kwargs)

    @deprecated
    def updateData(self):
        return self.update_data()

    @deprecated
    def loadData(self):
        return self._load_data()
