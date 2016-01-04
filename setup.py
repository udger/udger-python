import sys
from setuptools import setup

extra = {}
if sys.version_info < (2, 7):
    extra['install_requires'] = ['ordereddict']

setup(
    name='udger',
    version='1.0.0',
    author='The Udger Team',
    license='BSD',
    author_email='info@udger.com',
    description="Fast and reliable User Agent parser for Python.",
    long_description=__doc__,
    url='https://github.com/udger/udger-python',
    packages=['udger'],
    platforms='any',
    zip_safe=True,
    **extra
)
