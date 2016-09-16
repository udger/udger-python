import csv
import json
import operator
import sys

from udger import Udger

try:
    reduce
except NameError:
    from functools import reduce  # Python 3

"""
Running in both Python 2 and Python 3 like this:

$ PYTHONPATH=../.. python2 runtests.py
$ PYTHONPATH=../.. python3 runtests.py

Compare Python 2 to Python 3:
$ diff <(PYTHONPATH=../.. python3 runtests.py | sort) <(PYTHONPATH=../.. python2 runtests.py | sort)

"""


def iter_compare_dicts(dict1, dict2, only_common_keys=False, comparison_op=operator.ne):
    """
    A generator for comparation of values in the given two dicts.

    Yields the tuples (key, pair of values positively compared).

    By default, the *difference* of values is evaluated using the usual != op, but can be changed
    by passing other comparison_op (a function of two arguments returning True/False).

    For example: operator.eq for equal values, operator.is_not for not identical objects.

    You can also require comparison only over keys existing in both dicts (only_common_keys=True).
    Otherwise, you will get the pair with the Python built-in Ellipsis placed for dict with
    that key missing. (Be sure to test for Ellipsis using the 'is' operator.)

    >>> d1 = dict(a=1, b=2, c=3)
    >>> d2 = dict(a=1, b=20, d=4)
    >>> dict(iter_compare_dicts(d1, d2, only_common_keys=True))
    {'b': (2, 20)}
    >>> dict(iter_compare_dicts(d1, d2, only_common_keys=True, comparison_op=operator.eq))
    {'a': (1, 1)}
    >>> dict(iter_compare_dicts(d1, d2))
    {'c': (3, Ellipsis), 'b': (2, 20), 'd': (Ellipsis, 4)}
    >>> dict(iter_compare_dicts(d1, d2, comparison_op=operator.eq))
    {'a': (1, 1), 'c': (3, Ellipsis), 'd': (Ellipsis, 4)}
    """
    keyset1, keyset2 = set(dict1), set(dict2)

    for key in (keyset1 & keyset2):
        pair = (dict1[key], dict2[key])
        if reduce(comparison_op, pair):
            yield key, pair

    if not only_common_keys:
        for key in (keyset1 - keyset2):
            yield key, (dict1[key], Ellipsis)
        for key in (keyset2 - keyset1):
            yield key, (Ellipsis, dict2[key])


header_written = False
writer = csv.writer(sys.stdout, delimiter=';', quotechar='"')


def do_tests(json_filepath, test_func):
    global header_written, writer

    for testcase in json.load(open(json_filepath)):
        test_string = testcase['test']['teststring']

        expected = testcase['ret']

        resolved = test_func(test_string)
        resolved.pop('crawler_last_seen', None)
        resolved.pop('ip_last_seen', None)

        for field, (value_expected, value_returned) in iter_compare_dicts(expected, resolved):
            if (value_expected or '') == (value_returned or '') == '':
                continue

            # this client replaces ' ' with '%20' in strings; ignore the mismatch with test data
            if value_expected is not Ellipsis and (value_expected or '').startswith('https://'):
                if value_expected.replace(' ', '%20') == value_returned:
                    continue

            # tolerate number in strings
            if str(value_returned) == value_expected:
                continue

            if not header_written:
                writer.writerow(('STRING', 'RESPONSE_FIELD', 'VALUE_EXPECTED', 'VALUE_RETURNED'))
                header_written = True

            writer.writerow((test_string, field, value_expected, value_returned))

udger = Udger()

do_tests('test_ua.json', udger.parse_ua)
do_tests('test_ip.json', udger.parse_ip)
