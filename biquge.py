# -*- coding: utf-8 -*-
import time

from bs4 import BeautifulSoup
import re
from config import loggerinfo as logger,loggererror
from novelsearch import parse_search
from utils.models import Bookchapter, Book
from utils.session_create import create_session
from utils.sqlbackends import session_scope
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
session = create_session()

mysql_client = create_engine(
    "mysql+pymysql://zww:msbasic31@" "192.168.188.114:3306/bailutest?charset=utf8",
    encoding="utf-8",
)
session_sql = sessionmaker(bind=mysql_client)
session1 = session_sql()


content_url = "https://www.biquge.cc/html/372/372982/"
search_url = "https://sou.xanbhx.com/search?siteid=biqugecc&q={}"


def not_empty(s):
    return s and s.strip()


def parse_biquge(url):
    r = session.get(url)
    soup = BeautifulSoup(r.text, "lxml")
    item = soup.find("dl")
    ddt = item.findChildren()
    chap = ""
    res = list()
    tem = 0
    for index,d in enumerate(ddt):
        if d.name == 'dt' and '最新' not in d.text.strip():
            tem = index
    for d in ddt[tem:]:
        if d.name == "dt":
            chap = d.text.strip()
        if d.name == "dd":
            title = chap + d.text.strip()
            href = d.a["href"]
            res.append((title, href))
    return res


def parse_content(url):
    while 1:
        try:
            r = session.get(url)
            break
        except:
            loggererror.error('there is an error on {}'.format(url))
            continue
    soup = BeautifulSoup(r.text, "lxml")
    content = soup.find("div", {"id": "content"})
    res = content.text
    index = res.find("chaptererr")
    content = res[0:index]
    s = '<!--divstyle="color:#f00">'
    tt = content
    if s in tt:
        tt = tt[tt.find(s) + len(s):]
    rr = re.split('\s', tt)
    rr = filter(not_empty, rr)
    rr = list(rr)
    return str(rr)


def insert_nove():
    books = session1.query(Book).all()
    session1.close()
    for book in books:
        resu = parse_search(search_url.format(book.title))
        for itemb in resu:
            if book.title == itemb[0] and "biquge" in itemb[1]:
                logger.info("the book is find {}".format(book.title))
                res_list = parse_biquge(itemb[1])
                i = 1
                for item in res_list:
                    url = itemb[1] + item[1]
                    logger.info("the parse url is {}".format(url))
                    content = parse_content(url)
                    bc = Bookchapter(
                        id=None,
                        book_id=book.id,
                        title=item[0],
                        time_created=int(round(time.time())),
                        total_words=len(content),
                        content=content,
                        source_site_index=i,
                    )
                    with session_scope() as session:
                        status = session.add(bc)
                        logger.info('the status {}'.format(status))
                    i = i + 1



insert_nove()

