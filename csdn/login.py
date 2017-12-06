# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup

# 获取登陆时所需要的表单数据（可以用 fiddler 查看）
def get_post_data():
    login_page = s.get(url, headers=headers).text
    soup = BeautifulSoup(login_page, 'html.parser')
    lt = soup.find(attrs={'name': 'lt'})['value']
    execution = soup.find(attrs={'name': 'execution'})['value']
    submit = soup.find(attrs={'name': '_eventId'})['value']
    data = {
        'username': '*******',
        'password': '*******',
        'lt': lt,
        'execution': execution,
        '_eventId': submit
    }
    return data

if __name__ == '__main__':
    url = 'https://passport.csdn.net/account/login?from=http://my.csdn.net/my/mycsdn'
    s = requests.Session()
    headers = {
        'Host': 'passport.csdn.net',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Connection': 'keep-alive',
        'Referer': 'http://www.csdn.net/'
    }
    data = get_post_data()
    s.post(url, data=data, headers=headers)
    home_page = 'http://my.csdn.net/my/mycsdn'
    header = {
        'Host': 'my.csdn.net',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0',
        'Upgrade-Insecure-Requests': '1',
        'Accept': 'Accept'
    }
    response = s.get(home_page, headers=header)
    print(response.text)
