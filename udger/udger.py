import os
import platform
import socket
import time

try:
    import cPickle as pickle
except ImportError:
    import pickle

try:
    from urllib2 import urlopen, URLError
except ImportError:
    from urllib.request import urlopen, URLError

from .ini_data_loader import IniDataLoader
from .matcher import UdgerMatcher
from .constants import INI_FILE_URL_TEMPLATE, DEFAULT_TMP_DIR, VERSION


_CACHE_FILE_NAME = 'udger_{lib_version}_{python_version}.pickle.cache'


class UdgerException(Exception):
    pass


class Udger(object):

    def __init__(self, access_key, cache_dir=None, cache_ttl=None):
        """
        Args:
            cache_dir: String, path to the cache dir for useragent parsing data, default is /tmp.
            cache_ttl: Int, ttl for useragent parsing data cache in seconds, default is never.
                       Cache ttl is only checked on init when data is loaded.
        """

        self._cache_file_name = self._get_cache_file_name(cache_dir)
        self._cache_ttl = cache_ttl

        self._ini_data_loader = IniDataLoader()
        self.matcher = None

        self._ini_url = INI_FILE_URL_TEMPLATE.format(access_key=access_key)

        self._load_data()

    def _get_cache_file_name(self, cache_dir):
        cache_dir = cache_dir or DEFAULT_TMP_DIR

        if not os.access(cache_dir, os.W_OK):
            raise UdgerException("Cache directory %s is not writable." % cache_dir)

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
            raise UdgerException("Excepted argument useragent is not given.")

        result = self.matcher.match(useragent)

        return result

    def _fetch_url(self, url):
        context = urlopen(url)
        return context

    def _check_cache(self):
        if not os.path.exists(self._cache_file_name):
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

        self.matcher = UdgerMatcher(cache_data['data'])

    def update_data(self):
        """
        Fetch useragent parsing data from https://udger.com/ and update local cache
        """
        try:
            ini_file = self._fetch_url(self._ini_url)
            ini_data = self._ini_data_loader.parse_ini_file(ini_file)
        except (socket.timeout, socket.error, socket.gaierror, URLError) as e:
            raise UdgerException("Failed to download the cache data: %r" % e)

        self.matcher = UdgerMatcher(ini_data)

        cache_data = {
            'data': ini_data,
            'timestamp': time.time(),
        }
        cache_file = open(self._cache_file_name, 'wb')
        pickle.dump(cache_data, cache_file, -1)

        return True

    def _load_data(self):
        if self._check_cache():
            self._load_cache()
        else:
            self.update_data()
