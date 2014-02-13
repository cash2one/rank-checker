#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# ---------------------------------------
# Created by: Jlfme<jlfgeek@gmail.com>
# Created on: 2014-02-13 22:32:18
# ---------------------------------------


def remove_utf8_bom(file_path):
    """去除文件头部的UTF-8 BOM"""

    bom = b'\xef\xbb\xbf'
    with open(file_path, 'rb') as f:
        if f.read(3) == bom:

            print('dddd')
            body = f.read()
            with open(file_path, 'wb') as wf:
                wf.write(body)
