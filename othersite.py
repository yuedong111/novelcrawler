# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import re
import requests
import time
from utils.sqlbackends import session_scope
from utils.models import Book
from utils.es_backends import EsBackends

search_url = "https://www.x23us.com/modules/article/search.php"
us23_url = "https://sou.xanbhx.com/search?siteid=23uscc&q={}"
test_url = "https://www.23us.cc/html/324/324121/"
cloo_url = "http://www.2cloo.com/sort-shuku_list/s0/o0/od0/st0/w0/u0/v0/p{}/"
anhei_url = "http://www.anyew.cn/sort-shuku_list/s0/o0/lt0/st0/w0/u0/v0/c0/p{}/"


def dingdian_search(url, data):
    q = {'searchkey': data, 'action': 'login',
         'submit': '', 'searchtype': 'keywords'}

    r = session.post(url, json=q)
    with open('tes.html', 'w') as f:
        print(r.text, file=f)


def crawle_book(url):
    r = requests.get(url, timeout=3)
    soup = BeautifulSoup(r.text, 'lxml')
    temp = soup.find("tbody", {'id': 'resultDiv'})
    tem = temp.find_all('tr')
    if len(tem) > 2:
        for item in tem:
            data = {}
            index = item.find('td', {'class': 'index'}).text
            tit = item.find('a', {'class': 'title'})
            title = tit.text
            href = tit['href']
            author = item.find('td', {'class': 'author'}).text
            total_words = item.find('td', {'class': 'words'}).text
            body = {
                "query": {
                    "bool": {
                        "must": {
                            "match": {"title": title.strip()},
                            "match": {"author": author.strip()},
                        }
                    }
                }
            }
            res = EsBackends("crawled_books", "bookinfo").search_data(body)
            if res["hits"]["total"] == 0:
                data['title'] = title.strip()
                data['author'] = author.strip()
                book = Book(id=None, author_name=author.strip(), title=title.strip(), description=href, total_words=total_words, time_created=int(time.time()))
                with session_scope() as session:
                    session.add(book)
                EsBackends("crawled_books", "bookinfo").index_data(data)
                print('find a book {}'.format(title))
                # tem = ['index', 'title', 'author', 'total_words']
                # for it in tem:
                #     if locals()[it]:
                #         print(locals()[it].text)


def crawl_book():
    i = 1
    while i < 263:
        url = anhei_url.format(i)
        crawle_book(url)
        i = i + 1


crawl_book()
