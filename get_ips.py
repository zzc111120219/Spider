#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2017-12-06 20:51:12
# @Author  : Your Name (you@example.org)
# @Link    : http://example.org
# @Version : $Id$

import re
import time
import requests
from bs4 import BeautifulSoup


class PROXY:

    def __init__(self, pagenum):
        self.pagenum = pagenum
        self.proxies = []
        self.useful_proxies = []
        self.base_url = 'http://www.xicidaili.com/nn/'
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'Host': 'www.xicidaili.com',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'
        }
    
    # 爬取每个页面上的ip代理
    def get_onepage_proxies(self, page):
        url = self.base_url + str(page)
        response = requests.get(url, headers = self.headers)
        soup = BeautifulSoup(response.text, 'lxml')
        ips = soup.select('#ip_list > tr')
        for ip in ips:
            try:
                ip = ip.select('td')
                host = ip[1].text
                port = ip[2].text
                proxy = 'http://' + host + ':' + port
                self.proxies.append({'http': proxy})
            except Exception as e:
                pass

    # 对指定页数进行爬取
    def get_allpages_proxies(self):
        for i in range(self.pagenum):
            self.get_onepage_proxies(i + 1)

    # 删选有效代理
    def test_proxy(self):
        self.get_allpages_proxies()
        test_url = 'http://www.baidu.com/'
        for proxy in self.proxies:
            try:
                response = requests.get(test_url, proxies = proxy, timeout = 1)
                self.useful_proxies.append(proxy)
            except Exception as e:
                pass
        return self.useful_proxies


if __name__ == '__main__':
    pagenum = 1
    test = PROXY(pagenum)
    proxies = test.test_proxy()
    print(proxies)

