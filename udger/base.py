import collections
import os
import re
import sys
import socket
import sqlite3
import struct
import tempfile

from .queries import Queries
from .wdetector import *


if sys.version_info.major == 3 and sys.version_info.minor >= 10:
    from collections.abc import MutableMapping
else:
    from collections import MutableMapping


unperlize_re = re.compile('^/?(.*)/([si]*)$')

def make_empty_row(columns_dict):
    return dict((col, None) for col in columns_dict)

class cached_property(object):
    """
    Decorator that converts a method with a single self argument into a
    property cached on the instance.
    """
    def __init__(self, func):
        self.func = func

    def __get__(self, instance, unused_type=None):
        if instance is None:
            return self
        res = instance.__dict__[self.func.__name__] = self.func(instance)
        return res


class LRUDict(collections.MutableMapping):
    def __init__(self, maxlen, *a, **k):
        self.maxlen = maxlen
        self.d = dict(*a, **k)
        while len(self) > maxlen:
            self.popitem()

    def __iter__(self):
        return iter(self.d)

    def __len__(self):
        return len(self.d)

    def __getitem__(self, k):
        return self.d[k]

    def __delitem__(self, k):
        del self.d[k]

    def __setitem__(self, k, v):
        if k not in self and len(self) == self.maxlen:
            self.popitem()
        self.d[k] = v

class IdRegString(object):
    def __init__(self, rowid, word_id, word2_id, pattern):
        self.rowid = rowid
        self.word_id = word_id
        self.word2_id = word2_id
        self.pattern = pattern

class UdgerBase(object):
    db_filename = 'udgerdb_v3.dat'

    _client_word_detector = None
    _os_word_detector = None
    _device_word_detector = None

    _client_regstring_list = None
    _os_regstring_list = None
    _device_regstring_list = None

    client_emptyrow = make_empty_row(Queries.client_columns)
    client_emptyrow.update(
        ua_class="Unrecognized",
        ua_class_code="unrecognized",
    )

    os_emptyrow = make_empty_row(Queries.os_columns)
    device_emptyrow = make_empty_row(Queries.device_columns)
    marketname_emptyrow = make_empty_row(Queries.marketname_columns)

    ip_datacenter_emptyrow = make_empty_row(Queries.ip_columns)
    ip_datacenter_emptyrow.update(
        make_empty_row(Queries.datacenter_columns),
        ip_ver=None,
    )

    def __init__(self, data_dir=None, lru_cache_size=10000):
        self.data_dir = data_dir or tempfile.gettempdir()
        self.regexp_cache = {}
        if lru_cache_size > 0:
            self.lru_cache = LRUDict(lru_cache_size)

    @staticmethod
    def dict_factory(cursor, row):
        return dict(
            (col[0], row[idx])
            for idx, col in enumerate(cursor.description)
        )

    perl_flags = {
        's': re.DOTALL,
        'i': re.IGNORECASE,
        'm': re.MULTILINE,
        'x': re.VERBOSE,
    }

    def regexp_func(self, expr, item):
        global unperlize_re

        expr_re = self.regexp_cache.get(expr)
        if expr_re is None:
            m = unperlize_re.match(expr)
            old_expr = expr
            flags = 0
            if m:
                # strip / from the beginning and /(si...) from the end
                expr, opts = m.groups()
                # this fails for unsupported Perl flag
                flags = sum(map(self.perl_flags.get, opts))

            expr_re = re.compile(expr, flags)
            self.regexp_cache[old_expr] = expr_re

        self.last_regexp_match = expr_re.search(item)  # this does not take flags!

        return bool(self.last_regexp_match)

    @cached_property
    def db_cursor(self):
        db_filepath = os.path.join(self.data_dir, self.db_filename)
        db = sqlite3.connect(db_filepath)
#        db.create_function("REGEXP", 2, self.regexp_func)

        cursor = db.cursor()
        cursor.row_factory = self.dict_factory

        return cursor

    @cached_property
    def client_regstring_list(self):
        if UdgerBase._client_regstring_list is None:
            UdgerBase._client_regstring_list = UdgerBase.prepare_regexp_struct(self.db_cursor, "udger_client_regex")
        return UdgerBase._client_regstring_list

    @cached_property
    def os_regstring_list(self):
        if UdgerBase._os_regstring_list is None:
            UdgerBase._os_regstring_list = UdgerBase.prepare_regexp_struct(self.db_cursor, "udger_os_regex")
        return UdgerBase._os_regstring_list

    @cached_property
    def device_regstring_list(self):
        if UdgerBase._device_regstring_list is None:
            UdgerBase._device_regstring_list = UdgerBase.prepare_regexp_struct(self.db_cursor, "udger_deviceclass_regex")
        return UdgerBase._device_regstring_list

    @staticmethod
    def prepare_regexp_struct(db_cursor, regexp_table_name):
        result = []
        global unperlize_re
        for row in db_cursor.execute('SELECT rowid, regstring, word_id, word2_id FROM %s ORDER BY sequence' % regexp_table_name):
            regstring = row['regstring']
            m = unperlize_re.match(regstring)
            flags = 0
            if m:
                # strip / from the beginning and /(si...) from the end
                regstring, opts = m.groups()
                # this fails for unsupported Perl flag
                flags = sum(map(UdgerBase.perl_flags.get, opts))
            expr_re = re.compile(regstring, flags)
            rs = IdRegString(row['rowid'], row['word_id'], row['word2_id'], expr_re)
            result.append(rs)

        return result;

    @cached_property
    def client_word_detector(self):
        if UdgerBase._client_word_detector is None:
            UdgerBase._client_word_detector = UdgerBase.create_word_detector(self.db_cursor, 'udger_client_regex', 'udger_client_regex_words')
        return UdgerBase._client_word_detector

    @cached_property
    def device_word_detector(self):
        if UdgerBase._device_word_detector is None:
            UdgerBase._device_word_detector = UdgerBase.create_word_detector(self.db_cursor, 'udger_deviceclass_regex', 'udger_deviceclass_regex_words')
        return UdgerBase._device_word_detector

    @cached_property
    def os_word_detector(self):
        if UdgerBase._os_word_detector is None:
            UdgerBase._os_word_detector = UdgerBase.create_word_detector(self.db_cursor, 'udger_os_regex', 'udger_os_regex_words')
        return UdgerBase._os_word_detector

    @staticmethod
    def create_word_detector(db_cursor, regex_table, word_table_name):
        wdetector = WordDetector()
        sql = "SELECT %s FROM " + regex_table
        used_words = set(row['word_id'] for row in db_cursor.execute(sql % 'word_id'))
        used_words |= set(row['word2_id'] for row in db_cursor.execute(sql % 'word2_id'))

        for row in db_cursor.execute('SELECT * FROM %s' % word_table_name):
            if row['id'] in used_words:
                wdetector.add_word(row['id'], row['word'])

        return wdetector

    def db_get_first_row(self, sql, *params):
#        self.last_regexp_match = None

        self.db_cursor.execute(sql, params)

        for row in self.db_cursor:
            return row

    def db_iter_rows(self, sql, *params):
#        self.last_regexp_match = None

        self.db_cursor.execute(sql, params)

        for row in self.db_cursor:
            yield row

#            self.last_regexp_match = None

    @staticmethod
    def normalize_ipaddress(ip_string):
        try:
            packed = socket.inet_pton(socket.AF_INET, ip_string)
            ip_string = socket.inet_ntop(socket.AF_INET, packed)

            ipv6_words = None
            ipv4_int = struct.unpack("!L", packed)[0]
        except socket.error:
            packed = socket.inet_pton(socket.AF_INET6, ip_string)
            ip_string = socket.inet_ntop(socket.AF_INET6, packed)

            ipv6_words = struct.unpack("!8H", packed)
            ipv4_int = None

        return ip_string, ipv4_int, ipv6_words
