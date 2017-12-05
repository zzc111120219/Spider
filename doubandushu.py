#-*- coding: UTF-8 -*-

import re
import time
import random
import pymysql
import requests
import numpy as np
from bs4 import BeautifulSoup

# 获取 tags 页所有标签并组装成新的 url
def get_tags_url(url, headers):
    tags_url = []
    response = requests.get(url, headers = headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'lxml')
        # 右键检查提取 selector
        tags = soup.select("#content > div > div.article > div > div > table > tbody > tr > td > a")
        for tag in tags:
            tag = tag.get_text()
            tag_url = url + str(tag)
            tags_url.append(tag_url)
    return tags_url

# 对 scores 进行特别处理，如果少于十人评价，将导致 scores 获取出错
def get_scores(soup, length):
    num = 0
    persons = soup.select("#subject_list > ul > li > div.info > div.star.clearfix > span.pl")
    temps = soup.select("#subject_list > ul > li > div.info > div.star.clearfix > span.rating_nums")
    temps = list(map(lambda x:x.get_text(), temps))
    score_length = len(temps)
    if score_length == length:
        scores = list(map(lambda x:x.get_text(), soup.select("#subject_list > ul > li > div.info > div.star.clearfix > span.rating_nums")))
    else:
        scores = [persons[i].get_text().strip().strip('\(\)') for i in range(length)]
        for i in range(length):
            if scores[i] !='少于10人评价' and scores[i] !='目前无人评价':
                scores[i] = temps[num]
                num += 1
    return scores


# 输入一个标签的某一页，爬取该页面的相关信息
def get_one_page(url, headers):
    data = []
    response = requests.get(url, headers = headers)
    soup = BeautifulSoup(response.text.encode("utf-8"), "lxml")
    details = soup.select("#subject_list > ul > li > div.info > div.pub")
    titles = soup.select("#subject_list > ul > li > div.info > h2 > a")
    length = len(titles)
    scores = get_scores(soup, length)
    for detail, score, title in zip(details, scores, titles):
    	# 考虑到 detail 信息格式不一致，为避免索引带来的错误分类讨论
    	# 张惠辛 / 华夏出版社 / 2004 / 48.00
        if len(detail.get_text().split('/')) >= 4:
            author = detail.get_text().strip().split('/')[0].replace(' ', '')
            publisher = detail.get_text().strip().split('/')[-3].replace(' ', '')
            pub_date = detail.get_text().strip().split('/')[-2].replace(' ', '')
            price = detail.get_text().strip().split('/')[-1].replace(' ', '')
            title = title.get_text().strip().replace('\n', '').replace(' ', '')	
            score = score
            data.append([title, author, publisher, pub_date, price, score])
        # 张惠辛 / 2004 / 48.00
        if len(detail.get_text().split('/')) == 3:
            author = detail.get_text().strip().split('/')[0].replace(' ', '')
            publisher = ''
            pub_date = detail.get_text().strip().split('/')[-2].replace(' ', '')
            price = detail.get_text().strip().split('/')[-1].replace(' ', '')
            title = title.get_text().strip().replace('\n', '').replace(' ', '')
            score = score
            data.append([title, author, publisher, pub_date, price, score])
        # 2004 / 48.00
        if len(detail.get_text().split('/')) == 2:
            author = ''
            publisher = ''
            pub_date = detail.get_text().strip().split('/')[-2].replace(' ', '')
            price = detail.get_text().strip().split('/')[-1].replace(' ', '')
            title = title.get_text().strip().replace('\n', '').replace(' ', '')
            score = score
            data.append([title, author, publisher, pub_date, price, score])
    # 将 data 结果写入数据库
    sql = "INSERT INTO allbooks values(%s, %s, %s, %s, %s, %s)" 
    try:
        cursor.executemany(sql, data)
        db.commit()
    except:
        db.rollback()

# 输入某一标签下所有的页面结果
def get_all_pages(url, headers):
    _url = url
    response = requests.get(url, headers = headers)
    soup = BeautifulSoup(response.text.encode("utf-8"), "lxml")
    page_num = int(soup.select("#subject_list > div.paginator > a")[-1].get_text())
    for i in range(0, page_num):
        url = _url + "?start={}&type=T".format(str(i*20))
        print(url)
        get_one_page(url, headers)
        # 为防止频繁爬取 ip 被封，设置爬取间隔
        time.sleep(int(format(random.randint(0,9))))
  
if __name__=='__main__':
	# 连接数据库，并创建工作表
    db = pymysql.connect(host='localhost',user='root', password='********', database="python", use_unicode=True, charset="utf8")
    cursor = db.cursor()
    cursor.execute('DROP TABLE IF EXISTS allbooks')
    sql = """CREATE TABLE allbooks(      
        title CHAR(255) NOT NULL,      
        author CHAR(255),     
        publisher CHAR(255),     
        pub_date CHAR(255),     
        price CHAR(255),     
        score CHAR(255)       
        )"""
    cursor.execute(sql)
    url = "https://book.douban.com/tag/"
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'
    }
    tags_url = get_tags_url(url, headers)
    for tag_url in tags_url:
        get_all_pages(tag_url, headers)
    get_one_page(tag_url, headers)
    db.close()