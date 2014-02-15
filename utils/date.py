#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# ---------------------------------------
# Created by: Jlfme<jlfgeek@gmail.com>
# Created on: 2014-02-16 00:19:18
# ---------------------------------------


from datetime import datetime


def get_current_time():
    """ 获取当前系统日期时间字符串

    Returns:
        字符串格式日期: 2010-10-15 17:17:41
    """
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def get_current_date():
    """ 获取当前系统日期字符串

    Returns:
        字符串格式日期: 2010-10-15
    """
    return datetime.now().strftime('%Y-%m-%d')


def str_to_datetime(s):
    """ 获取当前系统日期字符串

    Args:
        s: 字符串形式的日期,例如: 10/Dec/2012:03:27:26

    Returns:
        datetime
    """
    return datetime.strptime(s, '%d/%b/%Y:%H:%M:%S')
