import re

try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict

from .constants import EMPTY_RESULT, INFO_URL


class IniDataLoader(object):

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
        section_pat = re.compile(r'^\[(\S+)\]$')
        option_pat = re.compile(r'^(\d+)\[\]\s=\s"(.*)"$')

        for line in file_buffer:
            line = line.decode('utf-8', 'ignore')
            option = option_pat.findall(line)
            if option:
                key = int(option[0][0])
                val = option[0][1]

                if key in data[current_section]:
                    data[current_section][key].append(val)
                else:
                    data[current_section][key] = [val]
            else:
                section = section_pat.findall(line)
                if section:
                    current_section = section[0]
                    data[current_section] = OrderedDict()

        return data

    def _get_matching_object(self, reg_list, details, details_template, browser_types=None, browser_os=None):
        m_data = []
        m_details = {}

        for k, r_obj in reg_list.items():
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
                if details_template[i] == 'ua_info_url':
                    det = INFO_URL + det

                if browser_types and details_template[i] == 'typ':
                    det = browser_types[int(det)][0]

                obj[details_template[i]] = det

            m_details[m_id] = obj

        return {
            'reg': m_data,
            'details': m_details,
        }

    def _get_robots_object(self, robots, os_details, browser_template, os_template):
        r_data = {}
        for r_id, robot in robots.items():
            obj = {}

            re = robot[0]
            details_browser = robot[1:7] + robot[8:]
            details_os = os_details[robot[7]] if robot[7] else []

            obj['ua'] = re
            obj['details'] = {'typ': 'Robot'}

            for i, name in enumerate(browser_template):
                det = details_browser[i] if len(details_browser) > i else EMPTY_RESULT[name]

                if name == 'ua_info_url':
                    det = INFO_URL + det

                obj['details'][name] = det

            for i, name in enumerate(os_template):
                det = details_os[i] if len(details_os) > i else EMPTY_RESULT[name]
                obj['details'][name] = det

            r_data[re] = obj

        return r_data

    def parse_ini_file(self, file_buffer):
        os_template = ['os_family', 'os_name', 'os_url', 'os_company', 'os_company_url', 'os_icon']
        browser_template = ['typ', 'ua_family', 'ua_url', 'ua_company', 'ua_company_url', 'ua_icon', 'ua_info_url']
        robot_template = ['ua_family', 'ua_name', 'ua_url', 'ua_company', 'ua_company_url', 'ua_icon', 'ua_info_url']
        device_template = ['device_type', 'device_icon', 'device_info_url']

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
