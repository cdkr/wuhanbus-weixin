#encoding:utf-8

import xml.etree.ElementTree as ET
import requests

KEY = '7931e48c2618c58d14fc11634f2867db'
TRANSFER_URL = u'http://openapi.aibang.com/bus/transfer?app_key=%s&city=武汉&start_addr=%s&end_addr=%s'
LINES_URL = u'http://openapi.aibang.com/bus/lines?app_key=%s&city=武汉&q=%s'
STATUS_URL = u'http://openapi.aibang.com/bus/stats?app_key=%s&city=武汉&q=%s'


def get_transfer(start_addr, end_attr):
    r = requests.get(TRANSFER_URL % (KEY, start_addr, end_attr))
    return _parse_info(r.content, 'bus')


def get_stats(stat):
    r = requests.get(STATUS_URL % (KEY, stat))
    return _parse_info(r.content, 'stat')


def get_lines(line):
    r = requests.get(LINES_URL % (KEY, line))
    return _parse_info(r.content, 'line')


def _parse_info(raw_str, tag):
    root = ET.fromstring(raw_str)

    data = [
        {child.tag: child.text for child in node}
        for node in root.getiterator(tag)
    ]

    return data
