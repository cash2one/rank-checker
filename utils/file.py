#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# ---------------------------------------
# Created by: Jlfme<jlfgeek@gmail.com>
# Created on: 2014-02-13 22:32:18
# ---------------------------------------


from inspect import isgenerator

from openpyxl.workbook import Workbook


def remove_utf8_bom(file_path):
    """去除文件头部的UTF-8 BOM"""

    bom = b'\xef\xbb\xbf'
    with open(file_path, 'rb') as f:
        if f.read(3) == bom:

            print('dddd')
            body = f.read()
            with open(file_path, 'wb') as wf:
                wf.write(body)


def int_to_letter(column):
    """ 将数字转化为excel的字母列，　例如　1 > A, 30 > AD
    # More information please visit http://support.microsoft.com/kb/833402
    """
    result = ""
    alpha = column // 27
    remainder = column - (alpha * 26)
    if alpha > 0:
        result = chr(alpha + 64)
    if remainder > 0:
        result += chr(remainder + 64)
    return result


class ExcelWriter(object):
    """ 创建Excel文件的工具类

    Attributes:
        filename: 文件名称,保存文件的时候使用
        title: 标题
    """

    def __init__(self, filename, title):

        self.filename = filename
        self.work = Workbook()
        self.chart = self.work.active
        # self.chart = self.work.create_sheet()
        self.chart.title = title

    def set_column_width(self, column_dict):
        if not isinstance(column_dict, dict):
            raise TypeError('column_dict must be a dictionary')
        for key, value in column_dict.items():
            self.chart.column_dimensions[key].width = column_dict[key]

    def add_content_cell(self, cell, value):
        self.chart[cell].value = value

    def add_content_row(self, row):
        """
        Args:
            row: must be a list, tuple
        """
        if not isgenerator(row) and not isinstance(row, (list, tuple, range)):
            raise TypeError('Value must be a list, tuple, range or a generator')
        self.chart.append(row)

    def save(self):
        self.work.save(self.filename + '.xlsx')
