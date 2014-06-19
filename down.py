# -*- coding: utf-8 -*-

import urllib2
import urllib
import re
import os
import threading
from pprint import pprint


def makedirs(url):
    """创建目录"""
    p = path(url)
    if not os.path.exists(p):
        os.makedirs(p)


def path(url):
    return '/'.join(url.split('/')[2:-1])


def filename(url):
    """根据url返回文件名"""
    url = url.split('?')[0]
    return '/'.join(url.split('/')[2:])


def htmlname(url):
    """Html文件名"""
    return filename(url) + '.html'


class Html(object):

    """docstring for Html"""

    def __init__(self, url):
        super(Html, self).__init__()
        self.url = url
        response = urllib2.urlopen(url)
        self.html = response.read().replace('="/', '="https://github.com/')

    def down(self):
        """ 下载url页面"""
        self.down_files()
        self.down_other_htmls()
        self.down_html()
        print 'Finish:', self.url

    def down_files(self):
        """下载url页面资源文件"""
        for url in self.findurls():
            if not os.path.exists(filename(url)):
                makedirs(url)
                while True:
                    try:
                        urllib.urlretrieve(url, filename(url))
                    except Exception, e:
                        print 'Exception:', url, filename(url)
                    else:
                        break

            self.html = self.html.replace(url, self.relative_path(url))

    def relative_path(self, url):
        """比较url返回相对路径"""
        main_path = re.compile(r'[^/]*').sub(r'..', path(self.url))
        return main_path + '/' + filename(url)

    def findurls(self):
        """查找所有的url资源"""
        l = re.compile(r'<link.*?>|src=".*?"').findall(self.html)
        return [re.compile(r'(href="|src=")(.*?)"').search(x).group(2) for x in l
                if re.match(r'.*//.*?/[^"]', x)]

    def down_other_htmls(self):
        """下载其他html页面"""
        for url in self.other_urls():
            if not os.path.exists(htmlname(url)):
                # print url
                Html(url).down()
            self.html = self.html.replace(
                url, self.relative_path(url) + '.html')

    def other_urls(self):
        """其他Html urls"""
        temp = re.compile(
            r'class="css-truncate css-truncate-target".*?</a>').findall(self.html)
        return [re.compile(r'.*href="(.*?)"').search(x).group(1)
                for x in temp]

    def down_html(self):
        """下载Html页面文件"""
        makedirs(self.url)
        with open(htmlname(self.url), 'wb') as f:
            f.write(self.html)


def down(url):
    h = Html(url)
    for x in branches_url(h.html):
        if not os.path.exists(htmlname(x)):
            threading.Thread(target=Html(x).down).start()
            # Html(x).down()
    h.down()


def branches_url(html):
    temp = re.compile(
        r'(?s)<a[^<>]*?js-navigation-open select-menu-item-text js-select-button-text css-truncate-target.*?/a>').findall(html)
    return [re.compile(r'.*href="(.*?)"').search(x).group(1)
            for x in temp]


url = 'https://github.com/michaelliao/awesome-python-webapp'
down(url)
