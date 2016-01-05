from os.path import dirname, join
import sys
from setuptools import setup

from udger.constants import VERSION

with open(join(dirname(__file__), 'README.md')) as readme_file:
    long_description = readme_file.read()


extra = {}
if sys.version_info < (2, 7):
    extra['install_requires'] = ['ordereddict']

setup(
    name='udger',
    version=VERSION,
    author='The Udger Team',
    license='BSD',
    author_email='info@udger.com',
    description="Fast and reliable User Agent parser for Python",
    long_description=long_description,
    url='https://github.com/udger/udger-python',
    packages=['udger'],
    platforms='any',
    zip_safe=True,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Libraries",
    ],
    **extra
)
