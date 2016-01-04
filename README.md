Fast and reliable User Agent parser for python
==============================================

Author: The Udger.com Team (info@udger.com)

- Tested with more the 50.000 unique user agents.
- Up to date data provided by https://udger.com/
- Support for python 3


Forked from:
---------

Based on the code by Jure Ham (jure.ham@zemanta.com),
https://github.com/hamaxx/uasparser2

Previously, a python version of https://github.com/kaittodesk/uasparser2
by Hicro Kee (http://hicrokee.com) email: hicrokee AT gmail DOT com
and modified by Michal Molhanec http://molhanec.net

Usage:
------

    $ git clone https://github.com/udger/udger-python
    $ cd udger.py/
    # python setup.py install
    $ mkdir /tmp/udger-cache
    $ python
    >>> from pprint import pprint
    >>> from udger import Udger
    >>> udger = Udger(
    ...     access_key='YOUR-ACCESS-KEY',
    ...     cache_dir='/tmp/udger-cache',
    ...     cache_ttl=3600*24*7,
    ... )
    >>> result = udger.parse(
    ...     'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, like Gecko) Version/9.0.2 Safari/601.3.9'
    ... )
    >>> pprint(result)
    {'device_icon': u'desktop.png',
     'device_info_url': u'/list-of-ua/device-detail?device=Personal computer',
     'device_type': u'Personal computer',
     'os_company': u'Apple Computer, Inc.',
     'os_company_url': u'http://www.apple.com/',
     'os_family': u'OS X',
     'os_icon': u'macosx.png',
     'os_name': u'OS X 10.11 El Capitan',
     'os_url': u'https://en.wikipedia.org/wiki/OS_X_El_Capitan',
     'type': u'Browser',
     'ua_company': u'Apple Inc.',
     'ua_company_url': u'http://www.apple.com/',
     'ua_family': u'Safari',
     'ua_icon': u'safari.png',
     'ua_info_url': u'https://udger.com/list-of-ua/browser-detail?browser=Safari',
     'ua_name': u'Safari 9.0.2',
     'ua_url': u'https://en.wikipedia.org/wiki/Safari_%28web_browser%29'}


