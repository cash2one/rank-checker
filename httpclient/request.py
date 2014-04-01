#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# ---------------------------------------
# Created by: Jlfme<jlfgeek@gmail.com>
# Created on: 2014-04-01 20:01:18
# ---------------------------------------


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
