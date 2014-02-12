#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# ---------------------------------------
# Created by: Jlfme<jlfgeek@gmail.com>
# Created on: 2014-02-03 21:09:18
# ---------------------------------------


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
    c.setopt(pycurl.CAINFO, certifi.where())   # https
    c.setopt(pycurl.FOLLOWLOCATION, 1)         # 自动跳转
    c.setopt(pycurl.MAXREDIRS, 5)              # 最大重定向数
    c.setopt(pycurl.ENCODING, 'gzip,deflate')  # Accept-Encoding

    agent = random_user_agent("browser")
    c.setopt(pycurl.USERAGENT, agent)          # User-Agent
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

    c.setopt(pycurl.URL, url)
    c.perform()

    return {
        'status': c.getinfo(pycurl.HTTP_CODE),
        'url': c.getinfo(pycurl.EFFECTIVE_URL),
        'effective_url': c.getinfo(pycurl.EFFECTIVE_URL),     # 实际作用的url, 如果有跳转
        'headers': header_stream.getvalue(),
        'body': body_stream.getvalue(),
        'ip': c.getinfo(pycurl.PRIMARY_IP)
    }
