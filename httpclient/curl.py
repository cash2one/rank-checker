#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# ---------------------------------------
# Created by: Jlfme<jlfgeek@gmail.com>
# Created on: 2014-03-20 19:44:18
# ---------------------------------------


import re
from collections import namedtuple
from io import BytesIO

import certifi
import pycurl

try:
    import signal
    from signal import SIGPIPE, SIG_IGN
    signal.signal(SIGPIPE, SIG_IGN)
except ImportError:
    pass

from httpclient.useragent import random_user_agent


# curl response
ResponseInfo = namedtuple(
    'ResponseInfo',
    field_names=[
        'status', 'ip', 'effective_url', 'total_time',
        'name_lookup_time', 'connect_time', 'pre_transfer_time',
        'start_transfer_time', 'redirect_time', 'size_upload',
        'size_download', 'speed_download', 'speed_upload',
        'header_size'
    ]
)


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
        curl.setopt(pycurl.TIMEOUT, 30)                                # 请求超时时间
        curl.setopt(pycurl.NOPROGRESS, True)                           # 是否屏蔽下载进度条，非0则屏蔽
        curl.setopt(pycurl.NOSIGNAL, True)

        # 自动跳转
        if settings.get('FOLLOW_LOCATION_ENABLED', True):
            curl.setopt(pycurl.FOLLOWLOCATION, 1)

        # 是否保持长连接
        if not settings.get('KEEP_ALIVE_ENABLED', True):
            curl.setopt(pycurl.FORBID_REUSE, 1)
            curl.setopt(pycurl.FRESH_CONNECT, 1)

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


class CurlRequestMixin(object):
    def process_request(self, request):
        curl = request.curl
        method = request.method

        if method == 'GET':
            pass
        elif method == 'POST':
            curl.setopt(pycurl.POSTFIELDS, request.data)
        elif method == 'HEAD':
            curl.setopt(pycurl.NOBODY, 1)

        # add header
        if request.headers:
            curl.setopt(pycurl.HTTPHEADER, request.headers)

        # add cookies
        if request.cookies:
            curl.setopt(pycurl.COOKIE, request.cookies)
            print('cookies:', request.cookies, request.url)

        # callback function for headers and body
        curl_response = CurlResponse()
        curl.setopt(pycurl.HEADERFUNCTION, curl_response.write_header)
        curl.setopt(pycurl.WRITEFUNCTION, curl_response.write_body)
        curl.setopt_string(pycurl.URL, request.url)

        try:
            curl.perform()
        except Exception as e:
            print(e)
        else:
            # 如果执行成功，绑定curl_response到curl
            curl.curl_response = curl_response


class CurlResponseMiXin(object):
    def process_response(self, curl):
        detail = self._detail_info(curl)
        curl_response = curl.curl_response
        headers = curl_response.headers()
        body = curl_response.body()

        # 最后清理工作
        self._clean(curl)

        return headers, body, detail

    def _detail_info(self, curl):
        # 获取response详细信息
        info = ResponseInfo(
            curl.getinfo(pycurl.HTTP_CODE),             # 返回的HTTP状态码
            curl.getinfo(pycurl.PRIMARY_IP),            # 返回IP地址
            curl.getinfo(pycurl.EFFECTIVE_URL),         # 重定向后的地址（实际起作用地址）
            curl.getinfo(pycurl.TOTAL_TIME),            # 传输结束所消耗的总时间
            curl.getinfo(pycurl.NAMELOOKUP_TIME),       # DNS解析所消耗的时间
            curl.getinfo(pycurl.CONNECT_TIME),          # 建立连接所消耗的时间
            curl.getinfo(pycurl.PRETRANSFER_TIME),      # 从建立连接到准备传输所消耗的时间
            curl.getinfo(pycurl.STARTTRANSFER_TIME),    # 从建立连接到传输开始消耗的时间
            curl.getinfo(pycurl.REDIRECT_TIME),         # 重定向所消耗的时间
            curl.getinfo(pycurl.SIZE_UPLOAD),           # 上传数据包大小
            curl.getinfo(pycurl.SIZE_DOWNLOAD),         # 下载数据包大小
            curl.getinfo(pycurl.SPEED_DOWNLOAD),        # 平均下载速度
            curl.getinfo(pycurl.SPEED_UPLOAD),          # 平均上传速度
            curl.getinfo(pycurl.HEADER_SIZE)            # HTTP头部大小
        )
        return info

    def _clean(self, curl):
        curl.unsetopt(pycurl.COOKIE)
        curl.unsetopt(pycurl.HTTPHEADER)

        if hasattr(curl, 'curl_response'):
            curl.curl_response.close()
            delattr(curl, 'curl_response')
