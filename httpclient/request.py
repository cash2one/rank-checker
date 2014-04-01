#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# ---------------------------------------
# Created by: Jlfme<jlfgeek@gmail.com>
# Created on: 2014-04-01 20:01:18
# ---------------------------------------


from urllib.parse import urlencode


class Request(object):

    def __init__(self, method=None, url=None, params=None,
                 data=None, headers=None, cookies=None, json=None):
        self.url = url
        self.method = method
        self.params = {} if params is None else params
        self.data = {} if data is None else data
        self.headers = {} if headers is None else headers
        self.cookies = {} if cookies is None else cookies
        self.json = json

    def __repr__(self):
        return '<Request [{}]>'.format(self.method)


class WrappedRequest(object):

    def __init__(self, method=None, url=None, params=None,
                 data=None, headers=None, cookies=None, json=None, curl=None):

        self.method = method
        self.url = url
        self.params = params
        self.data = data
        self.headers = headers
        self.cookies = cookies
        self.json = json
        self.curl = curl

        self._wrap_all()

    def __repr__(self):
        return '<WrappedRequest [method:{}] [url:{}]>'.format(
            self.method,
            self.url
        )

    def _wrap_all(self):
        self._wrap_method()
        self._wrap_url()
        self._wrap_data()
        self._warp_headers()
        self._wrap_cookies()

    def _wrap_method(self):
        if self.method is not None:
            self.method = self.method.upper()

    def _wrap_url(self):
        query = '' if self.params is None else urlencode(self.params)
        self.url = '{}?{}'.format(self.url, query) if query else self.url

    def _wrap_data(self):
        if self.data is not None:
            self.data = urlencode(self.data)

    def _warp_headers(self):
        if self.headers is not None:
            headers = ['%s: %s' % (str(k), str(v)) for k, v in self.headers.items()]
            self.headers = headers

    def _wrap_cookies(self):
        if self.data is not None:
            cookies = "; ".join(
                ['%s=%s' % (k, v) for k, v in self.cookies.items()]
            )
            self.cookies = cookies
        else:
            self.cookies = ''
