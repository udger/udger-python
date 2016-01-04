from .constants import EMPTY_RESULT


class UdgerMatcher(object):

    def __init__(self, data):
        self._data = data

    def _match_robots(self, useragent, result):
        try:
            res = self._data['robots'][useragent]
            result.update(res['details'])
            return True
        except KeyError:
            return False

    def _match_browser(self, useragent, result):
        for test in self._data['browser']['reg']:
            test_rg = test['re'].search(useragent)
            if test_rg:
                result.update(self._data['browser']['details'][test['details_key']])

                if test_rg.lastindex and test_rg.lastindex > 0:
                    browser_version = test_rg.group(1)
                    result['ua_name'] = '%s %s' % (result['ua_family'], browser_version)
                else:
                    result['ua_name'] = result['ua_family']

                os_key = test['os_details_key']
                if os_key:
                    result.update(self._data['os']['details'][os_key])

                    return True
                return False

        return False

    def _match_os(self, useragent, result):
        for test in self._data['os']['reg']:
            if test['re'].search(useragent):
                result.update(self._data['os']['details'][test['details_key']])

                return True
        return False

    def _match_device(self, useragent, result):
        for test in self._data['device']['reg']:
            if test['re'].search(useragent):
                result.update(self._data['device']['details'][test['details_key']])
                return True

        # Try to match using the type
        if result['type'] in ("Other", "Library", "Validator", "Useragent Anonymizer"):
            result.update(self._data['device']['details'][1])
        elif result['type'] in ("Mobile Browser", "Wap Browser"):
            result.update(self._data['device']['details'][3])
        else:
            result.update(self._data['device']['details'][2])

        return False

    def match(self, useragent):
        result = dict(EMPTY_RESULT)

        self._match_robots(useragent, result) or \
            self._match_browser(useragent, result) or \
            self._match_os(useragent, result)

        self._match_device(useragent, result)

        return result
