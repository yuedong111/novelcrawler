# -*- coding: utf-8 -*-
import time

from bs4 import BeautifulSoup

from config import logger
from novelsearch import parse_search
from utils.models import Bookchapter, Book
from utils.session_create import create_session
from utils.sqlbackends import session_scope
import pymysql

session = create_session()

content_url = "https://www.biquge.cc/html/372/372982/"
search_url = "https://sou.xanbhx.com/search?siteid=biqugecc&q={}"

db = pymysql.connect("192.168.188.114", "zww", "msbasic31", "bailutest")
cursor = db.cursor()


def parse_biquge(url):
    r = session.get(url)
    soup = BeautifulSoup(r.text, "lxml")
    item = soup.find("dl")
    ddt = item.findChildren()
    chap = ""
    res = list()
    for d in ddt:
        if d.name == "dt":
            chap = d.text.strip()
        if d.name == "dd":
            title = chap + d.text.strip()
            href = d.a["href"]
            res.append((title, href))
    return res


def parse_content(url):
    r = session.get(url)
    soup = BeautifulSoup(r.text, "lxml")
    content = soup.find("div", {"id": "content"})
    res = content.text
    index = res.find("chaptererr")
    content = res[0:index]
    return content


def insert_nove():
    with session_scope() as session1:
        books = session1.query(Book).all()
    for book in books:
        resu = parse_search(search_url.format(book.title))
        if book.title in resu and "biquge" in resu[book.title]:
            logger.info("the book is find {}".format(book.title))
            res_list = parse_biquge(resu[book.title])
            i = 1
            for item in res_list:
                url = resu[book.title] + item[1]
                logger.info("the parse url is {}".format(url))
                content = parse_content(url)
                bc = Bookchapter(
                    id=None,
                    book_id=book.id,
                    title=book.title,
                    time_created=int(round(time.time())),
                    total_words=len(content),
                    content=content,
                    source_site_index=i,
                )
                with session_scope() as session:
                    session.add(bc)
                i = i + 1


insert_nove()
# with session_scope() as sessiond:
#     b = Bookchapter(id=None, book_id=2, title='edws', time_created=round(time.time()),
#                     total_words=232, content='232', source_site_index=1)
#     sessiond.add(b)
