"""
userparse2
    By Jure Ham (jure.ham@zemanta.com)

Based on:
    A python version of http://user-agent-string.info/download/UASparser

    By Hicro Kee (http://hicrokee.com)
    email: hicrokee AT gmail DOT com

    Modified by Michal Molhanec http://molhanec.net

Usage:
    from uasparser2 import UASparser

    uas_parser = UASparser('/path/to/your/cache/folder', mem_cache_size=1000)

    result = uas_parser.parse('YOUR_USERAGENT_STRING')
"""
__all__ = ['UASParser', 'UASparser', 'EMPTY_RESULT']

from .uasparser import UASParser
from .constants import EMPTY_RESULT

from .uasparser import UASparser  # deprecated
