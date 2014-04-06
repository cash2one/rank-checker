#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# ---------------------------------------
# Created by: Jlfme<jlfgeek@gmail.com>
# Created on: 2014-04-06 20:12:18
# ---------------------------------------


from httpclient.client import HttpClient


def request(method, url, **kwargs):
    with HttpClient() as client:
        return client.request(method=method, url=url, **kwargs)


def head(url, **kwargs):
    """Sends a HEAD request.
    """

    return request('head', url, **kwargs)


def get(url, params=None, **kwargs):
    """Sends a GET request.
    """

    return request('get', url, params=params, **kwargs)


def post(url, data=None, **kwargs):
    """Sends a POST request.

    """

    return request('post', url, data=data, **kwargs)


def session(**kwargs):
    return HttpClient(**kwargs)
