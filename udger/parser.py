from .base import UdgerBase


class Udger(UdgerBase):
    def parse_ua(self, ua_string):
        ua = self.db_get_first_row(self.crawler_sql, ua_string)
        if ua:
            del ua['class_id']
            del ua['client_id']
            class_id = 99
            client_id = -1
        else:
            ua = self.db_get_first_row(self.client_sql, ua_string)
            if ua:
                self.patch_versions(ua)
            else:
                ua = self.client_emptyrow.copy()

            class_id = ua.pop('class_id', -1)
            client_id = ua.pop('client_id', 0)

        opsys = self.db_get_first_row(self.os_sql, ua_string)
        if not opsys:
            if client_id != 0:
                opsys = self.db_get_first_row(self.client_os_sql, client_id)

        ua.update(opsys or self.os_emptyrow)

        dev = self.db_get_first_row(self.device_sql, ua_string)
        if not dev:
            if class_id != -1:
                dev = self.db_get_first_row(self.client_class_sql, class_id)

        ua.update(dev or self.device_emptyrow)

        ua['ua_string'] = ua_string

        return ua

    def patch_versions(self, ua):
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

    def parse_ip(self, ip_string):
        ip = self.ip_datacenter_emptyrow.copy()
        ip['ip'] = ip_string

        try:
            ip_string, ipv4_int = self.normalize_ipaddress(ip_string)
        except:
            pass
        else:
            ip.update(
                ip_classification="Unrecognized",
                ip_classification_code="unrecognized",
            )

            ip_row = self.db_get_first_row(self.ip_sql, ip_string)
            if ip_row:
                if ip_row['ip_classification_code'] != 'crawler':
                    ip_row.pop('crawler_family_info_url')

                ip.update(ip_row)

            if ipv4_int is not None:
                ip['ip_ver'] = 4
                dc = self.db_get_first_row(self.datacenter_sql, ipv4_int, ipv4_int)
                if dc:
                    ip.update(dc)

            else:
                ip['ip_ver'] = 6

        return ip
