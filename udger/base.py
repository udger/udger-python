import os
import re
import sqlite3
import socket
import struct
import tempfile

unperlize_re = re.compile('^/?(.*)/si$')


def join_sql_columns(columns_dict, set_index=None):
    def columns():
        for col_name, col_expression in columns_dict.items():
            if set_index is not None:
                col_expression = col_expression[set_index]

            if col_expression == col_name:
                yield col_name
            else:
                yield '{0} AS {1}'.format(col_expression or 'NULL', col_name)

    return ',\n            '.join(columns())


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


class UdgerBase(object):
    db_filename = 'udgerdb_v3.dat'

    _client_columns = {
        'client_id':                   (None,                          'client_id'),
        'class_id':                    (None,                          'class_id'),

        'ua_class':                    ('"Crawler"',                   'client_classification'),
        'ua_class_code':               ('"crawler"',                   'client_classification_code'),
        'ua':                          ('name',                        'name'),
        'ua_engine':                   (None,                          'engine'),
        'ua_version':                  ('ver',                         None),
        'ua_version_major':            ('ver_major',                   None),
        'crawler_last_seen':           ('last_seen',                   None),
        'crawler_respect_robotstxt':   ('respect_robotstxt',           None),
        'crawler_category':            ('crawler_classification',      None),
        'crawler_category_code':       ('crawler_classification_code', None),
        'ua_uptodate_current_version': (None,                          'uptodate_current_version'),
        'ua_family':                   ('family',                      'name'),
        'ua_family_code':              ('family_code',                 'name_code'),
        'ua_family_homepage':          ('family_homepage',             'homepage'),
        'ua_family_icon':              ('family_icon',                 'icon'),
        'ua_family_icon_big':          (None,                          'icon_big'),
        'ua_family_vendor':            ('vendor',                      'vendor'),
        'ua_family_vendor_code':       ('vendor_code',                 'vendor_code'),
        'ua_family_vendor_homepage':   ('vendor_homepage',             'vendor_homepage'),
        'ua_family_info_url':          ('"https://udger.com/resources/ua-list/bot-detail?bot=" || '
                                        'REPLACE(family, " ", "%20") || "#id" || udger_crawler_list.id',
                                        '"https://udger.com/resources/ua-list/browser-detail?browser=" || '
                                        'REPLACE(name, " ", "%20")'),
    }

    crawler_sql = """
        SELECT
            %s
        FROM
            udger_crawler_list
        LEFT JOIN
            udger_crawler_class ON udger_crawler_class.id = udger_crawler_list.class_id
        WHERE
            ua_string = ?
    """ % join_sql_columns(_client_columns, 0)

    client_emptyrow = make_empty_row(_client_columns)
    client_emptyrow.update(
        ua_class="Unrecognized",
        ua_class_code="unrecognized",
    )

    client_sql = """
        SELECT
            %s
        FROM
            udger_client_regex
        JOIN
            udger_client_list ON udger_client_list.id = udger_client_regex.client_id
        JOIN
            udger_client_class ON udger_client_class.id = udger_client_list.class_id
        WHERE
            ? REGEXP regstring
        ORDER BY
            sequence ASC
        LIMIT 1
    """ % join_sql_columns(_client_columns, 1)

    _os_columns = {
        'os_family':                  'family',
        'os_family_code':             'family_code',
        'os':                         'name',
        'os_code':                    'name_code',
        'os_homepage':                'homepage',
        'os_icon':                    'icon',
        'os_icon_big':                'icon_big',
        'os_family_vendor':           'vendor',
        'os_family_vendor_code':      'vendor_code',
        'os_family_vendor_homepage':  'vendor_homepage',
        'os_info_url':                '"https://udger.com/resources/ua-list/os-detail?os=" || '
                                      'REPLACE(name, " ", "%20")',
    }

    os_emptyrow = make_empty_row(_os_columns)

    os_sql = """
        SELECT
            %s
        FROM
            udger_os_regex
        JOIN
            udger_os_list ON udger_os_list.id = udger_os_regex.os_id
        WHERE
            ? REGEXP regstring
        ORDER BY
            sequence ASC
        LIMIT 1
    """ % join_sql_columns(_os_columns)

    client_os_sql = """
        SELECT
            %s
        FROM
            udger_client_os_relation
        JOIN
            udger_os_list ON udger_os_list.id = udger_client_os_relation.os_id
        WHERE
            client_id = ?
    """ % join_sql_columns(_os_columns)

    _device_columns = {
        'device_class':           'name',
        'device_class_code':      'name_code',
        'device_class_icon':      'icon',
        'device_class_icon_big':  'icon_big',
        'device_class_info_url':  '"https://udger.com/resources/ua-list/device-detail?device=" || '
                                  'REPLACE(name, " ", "%20")',
    }

    device_emptyrow = make_empty_row(_device_columns)

    device_sql = """
        SELECT
            %s
        FROM
            udger_deviceclass_regex
        JOIN
            udger_deviceclass_list ON udger_deviceclass_list.id = udger_deviceclass_regex.deviceclass_id
        WHERE
            ? REGEXP regstring
        ORDER BY
            sequence ASC
        LIMIT 1
    """ % join_sql_columns(_device_columns)

    client_class_sql = """
        SELECT
            %s
        FROM
            udger_deviceclass_list
        JOIN
            udger_client_class ON udger_client_class.deviceclass_id = udger_deviceclass_list.id
        WHERE
            udger_client_class.id = ?
    """ % join_sql_columns(_device_columns)

    _ip_columns = {
        'ip_classification':              'ip_classification',
        'ip_classification_code':         'ip_classification_code',
        'ip_last_seen':                   'ip_last_seen',
        'ip_hostname':                    'ip_hostname',
        'ip_country':                     'ip_country',
        'ip_country_code':                'ip_country_code',
        'ip_city':                        'ip_city',
        'crawler_name':                   'name',
        'crawler_ver':                    'ver',
        'crawler_ver_major':              'ver_major',
        'crawler_family':                 'family',
        'crawler_family_code':            'family_code',
        'crawler_family_homepage':        'family_homepage',
        'crawler_family_vendor':          'vendor',
        'crawler_family_vendor_code':     'vendor_code',
        'crawler_family_vendor_homepage': 'vendor_homepage',
        'crawler_family_icon':            'family_icon',
        'crawler_family_info_url':        '"https://udger.com/resources/ua-list/bot-detail?bot=" || '
                                          'REPLACE(family, " ", "%20") || "#id" || udger_crawler_list.id',
        'crawler_last_seen':              'last_seen',
        'crawler_category':               'crawler_classification',
        'crawler_category_code':          'crawler_classification_code',
        'crawler_respect_robotstxt':      'respect_robotstxt',
    }

    ip_sql = """
        SELECT
            %s
        FROM
            udger_ip_list
        JOIN
            udger_ip_class ON udger_ip_class.id=udger_ip_list.class_id
        LEFT JOIN
            udger_crawler_list ON udger_crawler_list.id=udger_ip_list.crawler_id
        LEFT JOIN
            udger_crawler_class ON udger_crawler_class.id=udger_crawler_list.class_id
        WHERE
            ip = ?
        ORDER BY
            sequence
    """ % join_sql_columns(_ip_columns)

    _datacenter_columns = {
        'datacenter_name':       'name',
        'datacenter_name_code':  'name_code',
        'datacenter_homepage':   'homepage',
    }

    ip_datacenter_emptyrow = make_empty_row(_ip_columns)
    ip_datacenter_emptyrow.update(
        make_empty_row(_datacenter_columns),
        ip_ver=None,
    )

    datacenter_sql = """
        SELECT
            %s
        FROM
            udger_datacenter_range
        JOIN
            udger_datacenter_list ON udger_datacenter_range.datacenter_id = udger_datacenter_list.id
        WHERE
            iplong_from <= ? AND iplong_to >= ?
    """ % join_sql_columns(_datacenter_columns)

    def __init__(self, data_dir=None):
        self.data_dir = data_dir or tempfile.gettempdir()
        self.regexp_cache = {}

    @staticmethod
    def dict_factory(cursor, row):
        return dict(
            (col[0], row[idx])
            for idx, col in enumerate(cursor.description)
        )

    def regexp_func(self, expr, item):
        global unperlize_re

        expr_re = self.regexp_cache.get(expr)

        if expr_re is None:
            m = unperlize_re.match(expr)
            old_expr = expr
            if m:
                expr = m.group(1)  # strip / from the beginning and /si from the end

            expr_re = re.compile(expr, re.I | re.S)
            self.regexp_cache[old_expr] = expr_re

        self.last_regexp_match = expr_re.search(item)

        return bool(self.last_regexp_match)

    @cached_property
    def db_cursor(self):
        db_filepath = os.path.join(self.data_dir, self.db_filename)
        db = sqlite3.connect(db_filepath)
        db.create_function("REGEXP", 2, self.regexp_func)

        cursor = db.cursor()
        cursor.row_factory = self.dict_factory

        return cursor

    def db_get_first_row(self, sql, *params):
        self.last_regexp_match = None

        self.db_cursor.execute(sql, params)

        for row in self.db_cursor:
            return row

    @staticmethod
    def normalize_ipaddress(ip_string):
        try:
            ip_string = socket.inet_ntop(socket.AF_INET, socket.inet_pton(socket.AF_INET, ip_string))
            ipv4_int = struct.unpack("!L", socket.inet_aton(ip_string))[0]
        except socket.error:
            ip_string = socket.inet_ntop(socket.AF_INET6, socket.inet_pton(socket.AF_INET6, ip_string))
            ipv4_int = None

        return ip_string, ipv4_int
