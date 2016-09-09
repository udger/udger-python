# Udger client for Python (data ver. 3)
Local parser is very fast and accurate useragent string detection solution. Enables developers to locally install and integrate a highly-scalable product.
We provide the detection of the devices (personal computer, tablet, Smart TV, Game console etc.), operating system and client SW type (browser, e-mail client etc.).
It also provides information about IP addresses (Public proxies, VPN services, Tor exit nodes, Fake crawlers, Web scrapers .. etc.)


- Tested with more the 50.000 unique user agents.
- Up to date data provided by https://udger.com/
- Support for Python 3
  
### Install using pip

	$ pip install udger


### Install from git repo

	$ git clone https://github.com/udger/udger-python
	$ cd udger-python/
	# python setup.py install

### Automatic updates download

- for autoupdate data use Udger data updater (https://udger.com/support/documentation/?doc=62)

### Help us

Feel free to send us a Pull Request on GitHub to help us make Udger for Python better.
Thank you!

### Usage

	$ python
	>>> from pprint import pprint
	>>> from udger import Udger
	>>> udger = Udger()
	>>>
	>>> result = udger.parse_ua(
	...     'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, like Gecko) Version/9.0.2 Safari/601.3.9'
	... )
	>>> pprint(result)
	{'crawler_category': None,
	 'crawler_category_code': None,
	 'crawler_last_seen': None,
	 'crawler_respect_robotstxt': None,
	 'device_class': 'Desktop',
	 'device_class_code': 'desktop',
	 'device_class_icon': 'desktop.png',
	 'device_class_icon_big': 'desktop_big.png',
	 'device_class_info_url': 'https://udger.com/resources/ua-list/device-detail?device=Desktop',
	 'os': 'OS X 10.11 El Capitan',
	 'os_code': 'osx_10_11',
	 'os_family': 'OS X',
	 'os_family_code': 'osx',
	 'os_family_vendor': 'Apple Computer, Inc.',
	 'os_family_vendor_code': 'apple_inc',
	 'os_family_vendor_homepage': 'http://www.apple.com/',
	 'os_homepage': 'https://en.wikipedia.org/wiki/OS_X_El_Capitan',
	 'os_icon': 'macosx.png',
	 'os_icon_big': 'macosx_big.png',
	 'os_info_url': 'https://udger.com/resources/ua-list/os-detail?os=OS%20X%2010.11%20El%20Capitan',
	 'ua': 'Safari 9.0.2',
	 'ua_class': 'Browser',
	 'ua_class_code': 'browser',
	 'ua_engine': 'WebKit',
	 'ua_family': 'Safari',
	 'ua_family_code': 'safari',
	 'ua_family_homepage': 'https://en.wikipedia.org/wiki/Safari_%28web_browser%29',
	 'ua_family_icon': 'safari.png',
	 'ua_family_icon_big': 'safari_big.png',
	 'ua_family_info_url': 'https://udger.com/resources/ua-list/browser-detail?browser=Safari',
	 'ua_family_vendor': 'Apple Inc.',
	 'ua_family_vendor_code': 'apple_inc',
	 'ua_family_vendor_homepage': 'http://www.apple.com/',
	 'ua_string': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) '
		      'AppleWebKit/601.3.9 (KHTML, like Gecko) Version/9.0.2 '
		      'Safari/601.3.9',
	 'ua_uptodate_current_version': '9',
	 'ua_version': '9.0.2',
	 'ua_version_major': '9'}
	>>>
	>>> result = udger.parse_ua('Some thing')
	>>> pprint(result)
	{'crawler_category': None,
	 'crawler_category_code': None,
	 'crawler_last_seen': None,
	 'crawler_respect_robotstxt': None,
	 'device_class': None,
	 'device_class_code': None,
	 'device_class_icon': None,
	 'device_class_icon_big': None,
	 'device_class_info_url': None,
	 'os': None,
	 'os_code': None,
	 'os_family': None,
	 'os_family_code': None,
	 'os_family_vendor': None,
	 'os_family_vendor_code': None,
	 'os_family_vendor_homepage': None,
	 'os_homepage': None,
	 'os_icon': None,
	 'os_icon_big': None,
	 'os_info_url': None,
	 'ua': None,
	 'ua_class': 'Unrecognized',
	 'ua_class_code': 'unrecognized',
	 'ua_engine': None,
	 'ua_family': None,
	 'ua_family_code': None,
	 'ua_family_homepage': None,
	 'ua_family_icon': None,
	 'ua_family_icon_big': None,
	 'ua_family_info_url': None,
	 'ua_family_vendor': None,
	 'ua_family_vendor_code': None,
	 'ua_family_vendor_homepage': None,
	 'ua_string': 'Some thing',
	 'ua_uptodate_current_version': None,
	 'ua_version': None,
	 'ua_version_major': None}
	>>>
	>>> result = udger.parse_ip('69.89.31.120')
	>>> pprint(result)
	{'crawler_category': None,
	 'crawler_category_code': None,
	 'crawler_family': None,
	 'crawler_family_code': None,
	 'crawler_family_homepage': None,
	 'crawler_family_icon': None,
	 'crawler_family_info_url': None,
	 'crawler_family_vendor': None,
	 'crawler_family_vendor_code': None,
	 'crawler_family_vendor_homepage': None,
	 'crawler_last_seen': None,
	 'crawler_name': None,
	 'crawler_respect_robotstxt': None,
	 'crawler_ver': None,
	 'crawler_ver_major': None,
	 'datacenter_homepage': 'https://www.bluehost.com/',
	 'datacenter_name': 'Bluehost Inc.',
	 'datacenter_name_code': 'bluehost',
	 'ip': '69.89.31.120',
	 'ip_city': 'Provo',
	 'ip_classification': 'Web scraper',
	 'ip_classification_code': 'web_scraper',
	 'ip_country': 'United States',
	 'ip_country_code': 'US',
	 'ip_hostname': 'box320.bluehost.com',
	 'ip_last_seen': '2016-04-08 09:25:51',
	 'ip_ver': 4}
	>>>
	>>> result = udger.parse_ip('108.61.199.93')
	>>> pprint(result)
	{'crawler_category': 'Site monitor',
	 'crawler_category_code': 'site_monitor',
	 'crawler_family': 'PINGOMETER',
	 'crawler_family_code': 'pingometer',
	 'crawler_family_homepage': '',
	 'crawler_family_icon': 'bot_pingometer.png',
	 'crawler_family_info_url': 'https://udger.com/resources/ua-list/bot-detail?bot=PINGOMETER#id20112',
	 'crawler_family_vendor': 'Pingometer, LLC',
	 'crawler_family_vendor_code': 'pingometer_llc',
	 'crawler_family_vendor_homepage': 'http://pingometer.com/',
	 'crawler_last_seen': '2016-04-08 09:15:47',
	 'crawler_name': 'PINGOMETER',
	 'crawler_respect_robotstxt': 'no',
	 'crawler_ver': '',
	 'crawler_ver_major': '',
	 'datacenter_homepage': 'https://www.choopa.com/',
	 'datacenter_name': 'Choopa, LLC.',
	 'datacenter_name_code': 'choopa',
	 'ip': '108.61.199.93',
	 'ip_city': 'Amsterdam',
	 'ip_classification': 'Crawler',
	 'ip_classification_code': 'crawler',
	 'ip_country': 'Netherlands',
	 'ip_country_code': 'NL',
	 'ip_hostname': '108.61.199.93.vultr.com',
	 'ip_last_seen': '2016-04-08 09:00:40',
	 'ip_ver': 4}
   
### Data directory

Udger() parser expects the data file to be placed in the system temporary
directory as returned by the tempfile.gettempdir().

You may override the path using the argument like this:

	udger = Udger('/var/cache/udger/')


### Forked from

Based on the code by Jure Ham (jure.ham@zemanta.com),
https://github.com/hamaxx/uasparser2

Previously, a python version of https://github.com/kaittodesk/uasparser2
by Hicro Kee (http://hicrokee.com) email: hicrokee AT gmail DOT com
and modified by Michal Molhanec http://molhanec.net

   
### Author
The Udger.com Team (info@udger.com)

### old v1 format
If you still use the previous format of the db (v1), please see the branch old_format_v1   
