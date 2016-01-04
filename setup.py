"""
uasparser2
----------

Fast and reliable User Agent parser.

Easy to use
```````````

::

    from uasparser2 import UASparser

    uas_parser = UASparser('/path/to/your/cache/folder', mem_cache_size=1000)

    result = uas_parser.parse('YOUR_USERAGENT_STRING')

    # If input data is not avaible in cache folde, UASparser will download and prepare it on init.
    # Force data update by calling:

    uas_parser.updateData()


Fast
````

::

    Parsing 100,000 real user agents (10,000 unique):

    original uasparser: 7264.2 sec
    uasparser2 without cache: 171.7 sec
    uasparser2 with cache(size 1000): 34.6 sec


Links
`````

* `GitHub Home <https://github.com/hamaxx/uasparser2/>`_
* `User Agent Database <http://user-agent-string.info/>`_

"""

import sys
from setuptools import setup

extra = {}
if sys.version_info < (2, 7):
    extra['install_requires'] = ['ordereddict']

setup(
    name='uasparser2',
    version='0.3.1',
    author='Jure Ham',
    license='BSD',
    author_email='jure.ham@zemanta.com',
    description="Fast and reliable User Agent parser for Python.",
    long_description=__doc__,
    url='https://github.com/hamaxx/uasparser2',
    packages=['uasparser2'],
    platforms='any',
    zip_safe=True,
    **extra
)
