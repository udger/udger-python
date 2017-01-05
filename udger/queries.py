
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

class Queries(object):
    client_columns = {
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
    """ % join_sql_columns(client_columns, 0)

    client_sql = """
        SELECT
            %s
        FROM
            udger_client_regex ur
        JOIN
            udger_client_list ON udger_client_list.id = ur.client_id
        JOIN
            udger_client_class ON udger_client_class.id = udger_client_list.class_id
        WHERE
            ur.rowid=?
    """ % join_sql_columns(client_columns, 1)

    os_columns = {
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

    os_sql = """
        SELECT
            %s
        FROM
            udger_os_regex ur
        JOIN
            udger_os_list ON udger_os_list.id = ur.os_id
        WHERE
            ur.rowid=?
    """ % join_sql_columns(os_columns)

    client_os_sql = """
        SELECT
            %s
        FROM
            udger_client_os_relation
        JOIN
            udger_os_list ON udger_os_list.id = udger_client_os_relation.os_id
        WHERE
            client_id = ?
    """ % join_sql_columns(os_columns)

    device_columns = {
        'device_class':           'name',
        'device_class_code':      'name_code',
        'device_class_icon':      'icon',
        'device_class_icon_big':  'icon_big',
        'device_class_info_url':  '"https://udger.com/resources/ua-list/device-detail?device=" || '
                                  'REPLACE(name, " ", "%20")',
    }

    device_sql = """
        SELECT
            %s
        FROM
            udger_deviceclass_regex ur
        JOIN
            udger_deviceclass_list ON udger_deviceclass_list.id = ur.deviceclass_id
        WHERE
            ur.rowid=?
    """ % join_sql_columns(device_columns)

    client_class_sql = """
        SELECT
            %s
        FROM
            udger_deviceclass_list
        JOIN
            udger_client_class ON udger_client_class.deviceclass_id = udger_deviceclass_list.id
        WHERE
            udger_client_class.id = ?
    """ % join_sql_columns(device_columns)

    devicename_sql = """
        SELECT
            id AS regex_id,
            regstring
        FROM
            udger_devicename_regex
        WHERE
            os_family_code = ? AND
            os_code IN ('-all-', ?)
        ORDER BY
            sequence
    """

    marketname_columns = {
        'device_marketname':       'marketname',
        'device_brand':            'brand',
        'device_brand_code':       'brand_code',
        'device_brand_homepage':   'brand_url',
        'device_brand_icon':       'icon',
        'device_brand_icon_big':   'icon_big',
        'device_brand_info_url':   '"https://udger.com/resources/ua-list/devices-brand-detail?brand=" || '
                                   'REPLACE(brand_code, " ", "%20")',
    }

    marketname_sql = """
        SELECT
            %s
        FROM
            udger_devicename_list
        JOIN
            udger_devicename_brand ON udger_devicename_brand.id = udger_devicename_list.brand_id
        WHERE
            regex_id = ? AND code = ?
        LIMIT 1
    """ % join_sql_columns(marketname_columns)

    ip_columns = {
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
    """ % join_sql_columns(ip_columns)

    datacenter_columns = {
        'datacenter_name':       'name',
        'datacenter_name_code':  'name_code',
        'datacenter_homepage':   'homepage',
    }

    datacenter_sql = """
        SELECT
            %s
        FROM
            udger_datacenter_range
        JOIN
            udger_datacenter_list ON udger_datacenter_range.datacenter_id = udger_datacenter_list.id
        WHERE
            iplong_from <= ? AND iplong_to >= ?
    """ % join_sql_columns(datacenter_columns)

    datacenter6_sql = """
        SELECT
            %s
        FROM
            udger_datacenter_range6
        JOIN
            udger_datacenter_list ON udger_datacenter_range6.datacenter_id = udger_datacenter_list.id
        WHERE
            iplong_from0 <= ? AND iplong_from1 <= ? AND iplong_from2 <= ? AND iplong_from3 <= ? AND
            iplong_from4 <= ? AND iplong_from5 <= ? AND iplong_from6 <= ? AND iplong_from7 <= ? AND
            iplong_to0 >= ? AND iplong_to1 >= ? AND iplong_to2 >= ? AND iplong_to3 >= ? AND
            iplong_to4 >= ? AND iplong_to5 >= ? AND iplong_to6 >= ? AND iplong_to7 >= ?
    """ % join_sql_columns(datacenter_columns)

