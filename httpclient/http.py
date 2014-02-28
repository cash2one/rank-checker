#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# ---------------------------------------
# Created by: Jlfme<jlfgeek@gmail.com>
# Created on: 2014-02-03 21:09:18
# ---------------------------------------

import re
from io import BytesIO
from urllib.parse import urlencode

import pycurl
import certifi

from .useragent import random_user_agent


def get_html(url, params=None):
    """
    Args:
        url: 要下载的url
        params: (optional)　Dictionary

    Returns:
        dict: 返回包含html各种信息的字典
    """
    query = '' if params is None else urlencode(params)
    url = '{}?{}'.format(url, query) if query else url

    c = pycurl.Curl()
    c.setopt(pycurl.URL, url)

    c.setopt(pycurl.CAINFO, certifi.where())                    # https
    c.setopt(pycurl.FOLLOWLOCATION, 1)                          # 自动跳转
    c.setopt(pycurl.MAXREDIRS, 5)                               # 最大重定向数
    c.setopt(pycurl.ENCODING, 'gzip,deflate')                   # Accept-Encoding
    c.setopt(pycurl.USERAGENT, random_user_agent("browser"))    # User-Agent
    c.setopt(pycurl.CONNECTTIMEOUT, 10)
    c.setopt(pycurl.DNS_CACHE_TIMEOUT, 10)
    c.setopt(pycurl.TIMEOUT, 300)

    # 自动处理cookies
    c.setopt(pycurl.COOKIEJAR, 'cookies-file')
    c.setopt(pycurl.COOKIEFILE, 'cookies-file')

    # header and body
    header_stream = BytesIO()
    body_stream = BytesIO()
    c.setopt(pycurl.HEADERFUNCTION, header_stream.write)
    c.setopt(pycurl.WRITEFUNCTION, body_stream.write)

    # perform
    c.perform()

    return {
        'status': c.getinfo(pycurl.HTTP_CODE),
        'url': c.getinfo(pycurl.EFFECTIVE_URL),
        'effective_url': c.getinfo(pycurl.EFFECTIVE_URL),     # 实际作用的url, 如果有跳转
        'headers': header_stream.getvalue(),
        'body': body_stream.getvalue(),
        'ip': c.getinfo(pycurl.PRIMARY_IP)
    }


def get_effective_url(url):
    """ 通过指定URL获取实际的URL（301, 302等等跳转后的地址）

    """
    c = pycurl.Curl()
    c.setopt(pycurl.URL, url)

    c.setopt(pycurl.CAINFO, certifi.where())  # https
    c.setopt(pycurl.MAXREDIRS, 5)  # 最大重定向数
    c.setopt(pycurl.ENCODING, 'gzip,deflate')  # Accept-Encoding
    c.setopt(pycurl.USERAGENT, random_user_agent("browser"))  # User-Agent
    c.setopt(pycurl.CONNECTTIMEOUT, 10)
    c.setopt(pycurl.DNS_CACHE_TIMEOUT, 10)
    c.setopt(pycurl.TIMEOUT, 300)

    # HEAD request
    c.setopt(pycurl.NOBODY, 1)
    header_stream = BytesIO()
    c.setopt(pycurl.HEADERFUNCTION, header_stream.write)

    # perform
    c.perform()

    headers = header_stream.getvalue().decode('utf-8')
    location_re = re.compile(r'Location:\s*(P?.*)\r\n', re.I)
    m = re.search(location_re, headers)
    location = m.group(1) if m else ''

    return location
