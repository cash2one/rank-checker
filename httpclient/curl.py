#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# ---------------------------------------
# Created by: Jlfme<jlfgeek@gmail.com>
# Created on: 2014-03-20 19:44:18
# ---------------------------------------


import re
from io import BytesIO

import pycurl
import certifi

from httpclient.useragent import random_user_agent


class CurlFactory(object):

    @classmethod
    def new_curl_from_settings(cls, **settings):
        curl = pycurl.Curl()
        curl.setopt(pycurl.CAINFO, certifi.where())                    # https
        curl.setopt(pycurl.MAXREDIRS, 5)                               # 最大重定向数
        curl.setopt(pycurl.ENCODING, 'gzip,deflate')                   # Accept-Encoding
        curl.setopt(pycurl.USERAGENT, random_user_agent("browser"))    # User-Agent
        curl.setopt(pycurl.CONNECTTIMEOUT, 10)                         # 连接的等待时间，设置为0则不等待
        curl.setopt(pycurl.DNS_CACHE_TIMEOUT, 3600)                    # DNS缓存时间
        curl.setopt(pycurl.TIMEOUT, 300)                               # 请求超时时间
        curl.setopt(pycurl.NOPROGRESS, 1)                              # 是否屏蔽下载进度条，非0则屏蔽

        # 自动跳转
        if settings.get('FOLLOW_LOCATION_ENABLED', True):
            curl.setopt(pycurl.FOLLOWLOCATION, 1)

        # 是否保持长连接
        if not settings.get('KEEP_ALIVE_ENABLED', True):
            curl.setopt(pycurl.FORBID_REUSE, 1)

        # 处理cookies
        if settings.get('COOKIES_ENABLED', False):
            curl.setopt(pycurl.COOKIEFILE, 'cookies-file')
            curl.setopt(pycurl.COOKIEJAR, 'cookies-file')

        # HTTP代理设置
        # [socks4|socks5|socks|http|https]://[ip]:[port] 例如: socks5://10.10.10.1:1080
        if settings.get('HTTP_PROXY_ENABLED', False):
            if settings.get('HTTP_PROXIES', False):
                proxy = settings.get('HTTP_PROXIES').split('://')
                proxy_type = 5 if proxy[0] in ['socks', 'socks4', 'socks5'] else 1
                proxy_url = proxy[1]
                curl.setopt(pycurl.PROXYTYPE, proxy_type)
                curl.setopt(pycurl.PROXY, proxy_url)
        return curl


class CurlResponse(object):

    # Http-Status-Line regex
    status_line_re = re.compile(b'(P?^HTTP/\d{1}\.\d{1})\s+(P?\d{3})\s+(P?.*)', re.I)

    # cookie regex
    cookie_re = re.compile(r'set-cookie:\s*(P?.*)', re.I)

    # header field regex
    header_field_re = re.compile(r'(P?^.*?):\s*(P?.*)', re.I)

    def __init__(self):
        self.__header_bytes = BytesIO()
        self.__body_bytes = BytesIO()
        self.__headers = None

    def write_header(self, *args, **kwargs):
        line = args[0]

        # 当curl重定向时，只处理最终的header
        if re.search(self.status_line_re, line):
            self.__header_bytes.truncate(0)
            self.__header_bytes.seek(0)
        self.__header_bytes.write(*args, **kwargs)

    def write_body(self, *args, **kwargs):
        self.__body_bytes.write(*args, **kwargs)

    def get_raw_header(self):
        return self.__header_bytes.getvalue()

    def headers(self):
        if self.__headers is not None:
            return self.__headers
        else:
            self.__headers = {}
            lines = self.__header_bytes.getvalue().splitlines()

            # pop status-line
            lines.pop(0)

            for line in lines:
                line = self.decode(line)
                if re.match(self.cookie_re, line):
                    raw_cookie = re.match(self.cookie_re, line).group(1)
                    if 'Set-Cookie' not in self.__headers.keys():
                        self.__headers['Set-Cookie'] = [raw_cookie]
                    else:
                        self.__headers['Set-Cookie'].append(raw_cookie)
                else:
                    m = re.match(self.header_field_re, line)
                    if m:
                        key = m.group(1)
                        value = m.group(2)
                        self.__headers[key] = value

            return self.__headers

    def decode(self, bytes, encoding='utf-8'):
        return bytes.decode(encoding)

    def body(self):
        return self.__body_bytes.getvalue()

    def close(self):
        if not self.__header_bytes.closed:
            self.__header_bytes.close()
        if not self.__body_bytes.closed:
            self.__body_bytes.close()
