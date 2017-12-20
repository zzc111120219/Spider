# -*- coding: utf-8 -*-

import re
import time
import pinyin
import random
import pymysql
import requests
from bs4 import BeautifulSoup



# 模拟登陆
def login():
    url = 'http://passport.lianjia.com/cas/login?service=http://user.sh.lianjia.com/index'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36',
    }
    response = session.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    lt = soup.find(attrs={'name': 'lt'})['value']
    execution = soup.find(attrs={'name': 'execution'})['value']
    submit = soup.find(attrs={'name': '_eventId'})['value']
    data = {
        'redirect': 'http://user.sh.lianjia.com/index',
        'verifyCode': '',
        'username': '*******',
        'password': '***********',
        'code': '',
        'lt': lt,
        'execution': execution,
        '_eventId': submit,
        
    }
    response = session.post(url, data=data, headers=headers)
    return session

# 个人需要这里只考虑2号线周围房源
def subway_lines(url, headers):
    url = url + 'li143685058/'
    response = session.get(url, headers=headers)
    soup = BeautifulSoup(response.text.encode("utf-8"), "lxml")
    subway = soup.select('#metroList > div.level2.gio_plate > div > a')[1:]
    subway_gahref = list(map(lambda x: x['gahref'], subway))
    # subway_name = list(map(lambda x: x.get_text(), subway))
    return subway_gahref

# 计算某一站地铁周围的房源
def get_part_details(url, headers, content):
    url = url + content + '/'
    print(url)
    _url = url
    response = session.get(url, headers=headers)
    soup = BeautifulSoup(response.text.encode("utf-8"), "lxml")
    #  获取该站房源的总页数
    last_page = soup.select('#js-ershoufangList > div.content-wrapper > div.content > div > div.c-pagination > a')
    first_page = soup.select('#js-ershoufangList > div.content-wrapper > div.content > div > div.c-pagination > span')
    # 有的页数没有数据，first_page列表为空，不需要处理数据
    if first_page:
        # 当页码只有一页和多页的时候，索引有差别分开讨论
        if len(last_page) == 0:
            page_num = int(list(map(lambda x: x.get_text(), first_page))[0])
        else:
            page_num = int(list(map(lambda x: x.get_text(), last_page))[-2])
        # 逐页爬取
        for page in range(page_num):
            url = _url + 'd' + str(page + 1)
            # print(url)
            response = session.get(url, headers=headers)
            soup = BeautifulSoup(response.text.encode("utf-8"), "lxml")
            row1 = list(map(lambda x: x.get_text(), soup.select('#js-ershoufangList > div.content-wrapper > div.content > div > ul > li > div > div.info-table > div > span.info-col.row1-text')))
            row2 = list(map(lambda x: x.get_text(), soup.select('#js-ershoufangList > div.content-wrapper > div.content > div > ul > li > div > div.info-table > div > span.info-col.row2-text')))
            row3 = list(map(lambda x: x.get_text(), soup.select('#js-ershoufangList > div.content-wrapper > div.content > div > ul > li > div > div.property-tag-container')))
            # 提取小区、房价、地铁站等信息
            total_price = list(map(lambda x: x.get_text(), soup.select('#js-ershoufangList > div.content-wrapper > div.content > div > ul > li > div > div.info-table > div > div > span.total-price.strong-num')))
            unit_price = list(map(lambda x: x.get_text().strip().replace("单价", "").replace("元/平", ""), soup.select('#js-ershoufangList > div.content-wrapper > div.content > div > ul > li > div > div.info-table > div > span.info-col.price-item.minor')))
            fangxing = list(map(lambda x: x.split('|')[0].strip(), row1))
            size = list(map(lambda x: x.split('|')[1].strip().replace("平", ""), row1))
            floor = list(map(lambda x: x.split('|')[2].strip(), row1))
            chaoxiang = list(map(lambda x: x.split('|')[3].strip() if len(x.split('|'))==4 else 'NULL', row1))
            xiaoqu = list(map(lambda x: x.split('|')[0].strip(), row2))
            weizhi = list(map(lambda x: x[0].strip() + ' ' + x[1].strip(), map(lambda x: x.split('|')[1:3], row2)))
            jianzaoshijian = list(map(lambda x: x.split('|')[3].strip() if len(x.split('|'))==4 else 'NULL', row2))
            distances = list(map(lambda x: x.strip().split()[0], row3))
            subway_line = list(map(lambda x: re.search('距离(\d+)号线', x).group(1) + '号线', distances))
            subway = list(map(lambda x: re.search('号线(.*?)\d', x).group(1), distances))
            distance = list(map(lambda x: re.search('站(.*)米', x).group(1), distances))
            # print(distance)
            data = zip(xiaoqu, weizhi, jianzaoshijian, fangxing, size, floor, chaoxiang, subway_line, subway, distance, unit_price, total_price)
            sql = "INSERT INTO lianjia values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)" 
            try:
                cursor.executemany(sql, data)
                db.commit()
            except:
                db.rollback()
            time.sleep(20 + random.random())

def get_all_details(url, headers, subway_gahref):
    for content in subway_gahref:
        get_part_details(url, headers, content)

if __name__ == '__main__':
    url = 'http://sh.lianjia.com/ditiefang/'
    session = requests.Session()
    session = login()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36',
    }
    # 连接数据库，并创建工作表
    db = pymysql.connect(host='localhost', user='root', password='********', database="python", use_unicode=True, charset="utf8")
    cursor = db.cursor()
    cursor.execute('DROP TABLE IF EXISTS lianjia')
    sql = """CREATE TABLE lianjia(      
        xiaoqu CHAR(255) NOT NULL,      
        weizhi CHAR(255),     
        jianzaoshijian CHAR(255),     
        fangxing CHAR(255),     
        size CHAR(255),     
        floor CHAR(255),     
        chaoxiang CHAR(255),     
        subway_line CHAR(255),     
        subway CHAR(255),     
        distance CHAR(255),     
        unit_price CHAR(255),     
        total_price CHAR(255)   
        )"""
    cursor.execute(sql)
    subway_gahref = subway_lines(url, headers)
    get_all_details(url, headers, subway_gahref)
    db.close()
