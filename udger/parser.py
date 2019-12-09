from .base import UdgerBase

from .queries import Queries

class Udger(UdgerBase):

    def parse_ua(self, ua_string):

        if self.lru_cache is not None:
            cached = self.lru_cache.get(ua_string, None)
            if cached is not None:
                return cached

        ua, class_id, client_id = self._client_detector(ua_string)
        is_crawler = (ua['ua_class'] == 'Crawler')

        opsys = self._os_detector(ua_string, client_id) if not is_crawler else None
        ua.update(opsys or self.os_emptyrow)

        dev = self._device_detector(ua_string, class_id) if not is_crawler else None
        ua.update(dev or self.device_emptyrow)

        marketname = None
        if not is_crawler and ua['os_family_code']:
            # must complete first so cursors don't collide
            rows = tuple(self.db_iter_rows(
                Queries.devicename_sql,
                ua['os_family_code'],
                ua['os_code'],
            ))

            for dn_row in rows:
                if self.regexp_func(dn_row['regstring'], ua_string):
                    match = self.last_regexp_match.group(1)

                    marketname = self.db_get_first_row(
                        Queries.marketname_sql,
                        dn_row['regex_id'],
                        match.strip(),
                    )
                    if marketname:
                        break

        ua.update(marketname or self.marketname_emptyrow)

        ua['ua_string'] = ua_string

        self.lru_cache[ua_string] = ua

        return ua

    def parse_ip(self, ip_string):
        ip = self.ip_datacenter_emptyrow.copy()
        ip['ip'] = ip_string

        try:
            ip_string, ipv4_int, ipv6_words = self.normalize_ipaddress(ip_string)
        except:
            pass
        else:
            ip.update(
                ip_classification="Unrecognized",
                ip_classification_code="unrecognized",
            )

            ip_row = self.db_get_first_row(Queries.ip_sql, ip_string)
            if ip_row:
                if ip_row['ip_classification_code'] != 'crawler':
                    ip_row.pop('crawler_family_info_url')

                ip.update(ip_row)

            if ipv4_int is not None:
                ip['ip_ver'] = 4
                dc = self.db_get_first_row(Queries.datacenter_sql, ipv4_int, ipv4_int)

            else:
                ip['ip_ver'] = 6
                ipv6_words *= 2
                dc = self.db_get_first_row(Queries.datacenter6_sql, *ipv6_words)

            if dc:
                ip.update(dc)

        return ip
    def _client_detector(self, ua_string):
        ua = self.db_get_first_row(Queries.crawler_sql, ua_string)
        if ua:
            del ua['class_id']
            del ua['client_id']
            class_id = 99
            client_id = -1
        else:
            rowid = self._find_id_from_list(ua_string, self.client_word_detector.find_words(ua_string), self.client_regstring_list)
            if rowid != -1:
                ua = self.db_get_first_row(Queries.client_sql, rowid)
                self._patch_versions(ua)
            else:
                ua = self.client_emptyrow.copy()
            class_id = ua.pop('class_id', -1)
            client_id = ua.pop('client_id', 0)
        return (ua, class_id, client_id)

    def _os_detector(self, ua_string, client_id):
        rowid = self._find_id_from_list(ua_string, self.os_word_detector.find_words(ua_string), self.os_regstring_list)
        if rowid != -1:
            return self.db_get_first_row(Queries.os_sql, rowid)
        return client_id != 0 and self.db_get_first_row(Queries.client_os_sql, client_id)

    def _device_detector(self, ua_string, class_id):
        rowid = self._find_id_from_list(ua_string, self.device_word_detector.find_words(ua_string), self.device_regstring_list)
        if rowid != -1:
            return self.db_get_first_row(Queries.device_sql, rowid)
        return class_id != -1 and self.db_get_first_row(Queries.client_class_sql, class_id)

    def _find_id_from_list(self, ua_string, found_client_words, reg_string_list):
        self.last_regexp_match = None
        for irs in reg_string_list:
            if (irs.word_id in found_client_words) and (irs.word2_id in found_client_words):
                m = irs.pattern.search(ua_string)
                if not m is None:
                    self.last_regexp_match = m
                    return irs.rowid
        return -1

    def _patch_versions(self, ua):
        if self.last_regexp_match:
            try:
                ver = self.last_regexp_match.group(1)
            except IndexError:
                ver = ''

            ua['ua_version'] = ver
            ua['ua'] += " " + ver
            ua['ua_version_major'] = ver.split('.')[0]
        else:
            ua['ua_version'] = ua['ua_version_major'] = None

