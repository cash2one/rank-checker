#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# ---------------------------------------
# Created by: Jlfme<jlfgeek@gmail.com>
# Created on: 2014-03-05 20:12:18
# ---------------------------------------


import re

from pyquery import PyQuery

from httpclient.http import get_html
from httpclient.http import get_effective_url
from data.rank import RankStorage


class BaiduChecker(object):
    """ 百度关键词排名查询

    Attributes:
        sites: (list) 要查询的网站列表
        keywords: (list) 关键词列表
        per_page: (int) 每页记录数
        page_nums: (int) 查询总页数
        intervals: (int) 查询间隔时间默认是0秒
    """

    def __init__(self, site, keywords, per_page=20,
                 page_nums=5, intervals=0):

        self.site = site
        self.keywords = keywords
        self.per_page = per_page
        self.page_nums = page_nums
        self.intervals = intervals

        # 查询结果
        self.rank_storage = RankStorage('baidu', self.site, keywords)

    def start(self):
        for keyword in self.keywords:
            self._check(keyword)
        print('<---查询结束--->')
        self.rank_storage.save_result()

    def _check(self, keyword):
        flag = False
        for page in range(0, self.page_nums):
            print('正在查询<百度PC>第{}页关键词[{}]'.format(page+1, keyword))
            pn = page * self.per_page if page > 0 else page
            params = {'rn': self.per_page, 'pn': pn, 'wd': keyword}

            body = get_html(url='http://www.baidu.com/s', params=params)['body']

            d = PyQuery(body)
            for item in d(".f13 .c-showurl").items():
                text = item.text().replace(' ', '')
                if re.search(re.compile(self.site, re.IGNORECASE), text):
                    flag = True
                    index = int(item.parents('.result').attr('id'))  # 排名
                    title = eval(item.next('.c-tools').attr('data-tools'))['title']
                    url = eval(item.next('.c-tools').attr('data-tools'))['url']
                    url = get_effective_url(url)
                    print('---> 排名:[{}] 网址:[{}] 标题:[{}]'.format(index, url, url))
                    self.rank_storage.add_rank(keyword, url, index)

            # 如果当前页面有排名，就结束该关键词查询
            if flag:
                break

        # 如果没有查询到，就添加默认数据
        if not flag:
            self.rank_storage.add_rank(keyword, self.site, self.page_nums * self.per_page)
