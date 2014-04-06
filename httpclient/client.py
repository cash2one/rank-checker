#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# ---------------------------------------
# Created by: Jlfme<jlfgeek@gmail.com>
# Created on: 2014-03-17 20:31:18
# ---------------------------------------


from copy import copy

from httpclient.curl import CurlFactory, CurlRequestMixin, CurlResponseMiXin
from httpclient.request import Request, WrappedRequest


DEFAULT_SETTINGS = {
    'FOLLOW_LOCATION_ENABLED': True,
    'KEEP_ALIVE_ENABLED': True,
    'COOKIES_ENABLED': False,
    'HTTP_PROXY_ENABLED': False,
    'HTTP_PROXIES': 'http://10.10.10.2:8888',
    'REQUEST_HEADERS': {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6,ja;q=0.4,fil;q=0.2,zh-TW;q=0.2'
    }
}



class HttpClient(CurlRequestMixin, CurlResponseMiXin):

    def __init__(self, **kwargs):
        self.settings = self.merge_settings(**kwargs)
        self.__curl = CurlFactory.new_curl_from_settings(**self.settings)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def merge_settings(self, **settings):
        new_settings = copy(DEFAULT_SETTINGS)
        new_settings.update(settings)
        return new_settings

    def request(self, method, url, params=None, data=None, headers=None, cookies=None, json=None):
        req = Request(
            method=method,
            url=url,
            params=params,
            data=data,
            headers=headers,
            cookies=cookies,
            json=json
        )
        wrapped_req = self.wrap_request(req)
        self.process_request(wrapped_req)

        response = self.process_response(wrapped_req.curl)
        print(response[2])

    def wrap_request(self, request):
        # merge headers
        headers = copy(request.headers)
        headers.update(self.settings['REQUEST_HEADERS'])

        req = WrappedRequest(
            request.method,
            request.url,
            request.params,
            request.data,
            headers,
            request.cookies,
            request.json,
            self.__curl
        )
        return req

    def close(self):
        self.__curl.close()
