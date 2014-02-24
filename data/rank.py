#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# ---------------------------------------
# Created by: Jlfme<jlfgeek@gmail.com>
# Created on: 2014-02-24 22:14:18
# ---------------------------------------

import os
from collections import namedtuple

from app import BASE_DIR
from utils.file import ExcelWriter
from utils.date import get_current_time, get_current_date


RankItem = namedtuple('RankItem', ['keyword', 'url', 'index'])


class RankStorage(object):
    """ 存储查询结果

    Attributes:
        engine: (str) 搜索引擎的名称 取值：baidu(百度PC), mbaidu(百度移动), so(360PC), mso(360移动)
        site: (str) 网站域名
        keywords: (list) 关键词列表
    """

    def __init__(self, engine, site, keywords):
        self.engine = engine
        self.site = site
        self.keywords = keywords
        self.results = []

    def add_rank(self, keyword, url, index):
        self.results.append(RankItem(keyword, url, index))

    def save_result(self, filename=None):
        print("正在导出查询结果......")

        if self.engine == 'baidu':
            title = '百度(PC)'
        elif self.engine == 'mbaidu':
            title = '百度(移动)'
        elif self.engine == 'so':
            title = '360(PC)'
        elif self.engine == 'mso':
            title = '360(移动)'
        else:
            title = '排名'

        # 如果文件夹不存在就创建
        file_dir = os.path.abspath(os.path.join(BASE_DIR, 'out'))
        if not os.path.exists(file_dir):
            os.mkdir(file_dir)

        name = filename or self.site
        filename = os.path.abspath(os.path.join(file_dir, name + get_current_date() + title))

        excel_writer = ExcelWriter(filename, title)
        excel_writer.add_content_row(['关键词|长尾关键词', '网址', '排名', '查询统计'])
        excel_writer.set_column_width({'A': 50.0, 'B': 50.0, 'C': 10.0, 'D': 35.0})

        top_count = 0  # 排名前10名的关键词总数量
        for rank in self.results:
            if rank.index <= 10:
                top_count += 1
            excel_writer.add_content_row(rank)

        # 处理结果写入文件中
        excel_writer.add_content_cell('D2', '搜索引擎：' + title)
        excel_writer.add_content_cell('D3', '查询网站：' + self.site)
        excel_writer.add_content_cell('D4', '关键词总数：' + str(len(self.keywords)))
        excel_writer.add_content_cell('D5', '前10名总数：' + str(top_count))
        excel_writer.add_content_cell('D6', '查询日期：' + get_current_time())
        excel_writer.save()
