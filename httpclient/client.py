#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# ---------------------------------------
# Created by: Jlfme<jlfgeek@gmail.com>
# Created on: 2014-03-17 20:31:18
# ---------------------------------------


import pycurl
import certifi

from httpclient.useragent import random_user_agent


class CurlFactory(object):

    @classmethod
    def new_curl_from_settings(cls, **settings):
        c = pycurl.Curl()
        c.setopt(pycurl.CAINFO, certifi.where())                    # https
        c.setopt(pycurl.MAXREDIRS, 5)                               # 最大重定向数
        c.setopt(pycurl.ENCODING, 'gzip,deflate')                   # Accept-Encoding
        c.setopt(pycurl.USERAGENT, random_user_agent("browser"))    # User-Agent

        c.setopt(pycurl.CONNECTTIMEOUT, 10)                         # 连接的等待时间，设置为0则不等待
        c.setopt(pycurl.DNS_CACHE_TIMEOUT, 10)                      # DNS缓存时间
        c.setopt(pycurl.TIMEOUT, 300)                               # 请求超时时间
        c.setopt(pycurl.NOPROGRESS, 0)                              # 是否屏蔽下载进度条，非0则屏蔽

        # 自动跳转
        if settings.get('FOLLOW_LOCATION_ENABLED', False):
            c.setopt(pycurl.FOLLOWLOCATION, 1)

        # 是否保持长连接
        if not settings.get('KEEP_ALIVE_ENABLED', False):
            c.setopt(pycurl.FORBID_REUSE, 1)

        # 处理cookies
        if settings.get('COOKIES_ENABLED', False):
            c.setopt(pycurl.COOKIEJAR, 'cookies-file')
            c.setopt(pycurl.COOKIEFILE, 'cookies-file')

        # HTTP代理设置
        # [socks4|socks5|socks|http|https]://[ip]:[port] 例如: socks5://10.10.10.1:1080
        if settings.get('HTTP_PROXY_ENABLED', False):
            if settings.get('HTTP_PROXIES', False):
                proxy = settings.get('HTTP_PROXIES').split('://')
                proxy_type = 5 if proxy[0] in ['socks', 'socks4', 'socks5'] else 1
                proxy_url = proxy[1]
                c.setopt(pycurl.PROXYTYPE, proxy_type)
                c.setopt(pycurl.PROXY, proxy_url)
        return c
