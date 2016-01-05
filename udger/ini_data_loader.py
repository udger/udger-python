import re

try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict

from .constants import EMPTY_RESULT, PROJECT_HOMEPAGE


class IniDataLoader(object):
    section_re = re.compile(r'^\[(\S+)\]$')
    option_re = re.compile(r'^(\d+)\[\]\s=\s"(.*)"$')

    info_patch_re = re.compile(r'^/list-of-ua/(.*)')

    def _to_python_reg(self, reg):
        reg_l = reg[1:reg.rfind('/')]
        reg_r = reg[reg.rfind('/') + 1:]
        flag = 0
        if 's' in reg_r:
            flag = flag | re.S
        if 'i' in reg_r:
            flag = flag | re.I

        return re.compile(reg_l, flag)

    def _read_ini_file(self, file_buffer):
        data = {}

        current_section = ''

        for line in file_buffer:
            line = line.decode('utf-8', 'ignore')
            option = self.option_re.findall(line)
            if option:
                key = int(option[0][0])
                val = option[0][1]

                if key in data[current_section]:
                    data[current_section][key].append(val)
                else:
                    data[current_section][key] = [val]
            else:
                section = self.section_re.findall(line)
                if section:
                    current_section = section[0]
                    data[current_section] = OrderedDict()

        return data

    def _patch_detail(self, name, det):
        if det is not None:
            if name in ('ua_udger_url', 'device_udger_url'):
                det = self.info_patch_re.sub(PROJECT_HOMEPAGE + r'/resources/ua-list/\1', det)
                det = det.replace(' ', '%20')

            elif '/' not in det:
                for k in 'device', 'ua', 'os':
                    if name == k + '_icon':
                        det = '/'.join((PROJECT_HOMEPAGE, 'pub', 'img', k, det))
                        break

        return det

    def _get_matching_object(self, reg_list, details, details_template, browser_types=None, browser_os=None):
        m_data = []
        m_details = {}

        for r_obj in reg_list.values():
            reg = self._to_python_reg(r_obj[0])
            m_id = int(r_obj[1])

            obj = {'re': reg, 'details_key': m_id, 'os_details_key': None}

            # OS details from browser
            if browser_os and m_id in browser_os:
                key = int(browser_os[m_id][0])
                obj['os_details_key'] = key

            m_data.append(obj)

        for m_id, details in details.items():
            obj = {}

            for i, det in enumerate(details):
                name = details_template[i]

                if name == 'type' and browser_types:
                    det = browser_types[int(det)][0]

                else:
                    det = self._patch_detail(name, det)

                obj[name] = det

            m_details[m_id] = obj

        return {
            'reg': m_data,
            'details': m_details,
        }

    def _get_robots_object(self, robots, os_details, browser_template, os_template):
        r_data = {}
        for robot in robots.values():
            obj = {}

            re = robot[0]
            details_browser = robot[1:7] + robot[8:]
            details_os = os_details[robot[7]] if robot[7] else []

            obj['ua'] = re
            obj['details'] = {'type': 'Robot'}

            for i, name in enumerate(browser_template):
                det = details_browser[i] if len(details_browser) > i else EMPTY_RESULT[name]

                det = self._patch_detail(name, det)

                obj['details'][name] = det

            for i, name in enumerate(os_template):
                det = details_os[i] if len(details_os) > i else EMPTY_RESULT[name]

                det = self._patch_detail(name, det)

                obj['details'][name] = det

            r_data[re] = obj

        return r_data

    def parse_ini_file(self, file_buffer):
        os_template = ['os_family', 'os_name', 'os_url', 'os_company', 'os_company_url', 'os_icon']
        browser_template = ['type', 'ua_family', 'ua_url', 'ua_company', 'ua_company_url', 'ua_icon', 'ua_udger_url']
        robot_template = ['ua_family', 'ua_name', 'ua_url', 'ua_company', 'ua_company_url', 'ua_icon', 'ua_udger_url']
        device_template = ['device_name', 'device_icon', 'device_udger_url']

        data = self._read_ini_file(file_buffer)

        robots = self._get_robots_object(data['robots'], data['os'], robot_template, os_template)
        os = self._get_matching_object(data['os_reg'], data['os'], os_template)
        browser = self._get_matching_object(
            data['browser_reg'], data['browser'], browser_template, data['browser_type'], data['browser_os']
        )
        device = self._get_matching_object(data['device_reg'], data['device'], device_template)

        return {
            'robots': robots,
            'os': os,
            'browser': browser,
            'device': device,
        }
