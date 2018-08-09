# -*- coding: utf-8 -*-
from utils.session_create import create_session
from bs4 import BeautifulSoup
from utils.sqlbackends import session_scope
from utils.models import Bookchapter, Book
from novelsearch import parse_search
import time
session = create_session()

content_url = 'https://www.biquge.cc/html/372/372982/'
search_url = 'https://sou.xanbhx.com/search?siteid=biqugecc&q={}'

def parse_biquge(url):
    r = session.get(url)
    soup = BeautifulSoup(r.text, 'lxml')
    item = soup.find('dl')
    ddt = item.findChildren()
    chap = ''
    res = list()
    for d in ddt:
        if d.name == 'dt':
            chap = d.text.strip()
        if d.name == 'dd':
            title = chap + d.text.strip()
            href = d.a['href']
            res.append((title, href))
    return res


def parse_content(url):
    r = session.get(url)
    soup = BeautifulSoup(r.text, 'lxml')
    content = soup.find('div', {'id': 'content'})
    res = content.text
    index = res.find('chaptererr')
    content = res[0: index]
    return content


def insert_nove():
    with session_scope() as session:
        books = (
            session.query(Book).all()
        )
        for book in books:
            resu = parse_search(search_url.format(book.title))
            if book.title in resu and 'biquge' in resu[book.title]:
                res_list = parse_biquge(resu[book.title])
                i = 1
                for item in res_list:
                    url = resu[book.title] + '/' + item[1]
                    content = parse_content(url)
                    b = Bookchapter(id=None, book_id=book.id, title=book.title, time_created=round(time.time()),
                                    total_words=len(content), content=content, source_site_index=1)
                    session.add(b)
                    i = i + 1


insert_nove()