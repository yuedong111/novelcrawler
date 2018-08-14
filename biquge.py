# -*- coding: utf-8 -*-
import time

from bs4 import BeautifulSoup
import re
from config import loggerinfo as logger, loggererror
from tools.novelsearch import parse_search
from utils.models import Bookchapter, Book
from utils.session_create import create_session
from utils.sqlbackends import session_scope
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from utils.es_backends import EsBackends
from datetime import datetime
from hashlib import md5

session = create_session()

mysql_client = create_engine(
    "mysql+pymysql://zww:msbasic31@" "192.168.188.114:3306/bailutest?charset=utf8",
    encoding="utf-8",
)

session_sql = sessionmaker(bind=mysql_client)
session1 = session_sql()

content_url = "https://www.biquge.cc/html/372/372982/"
search_url = "https://sou.xanbhx.com/search?siteid={0}&q={1}"


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
    for index, d in enumerate(ddt):
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
    count = 0
    while 1:
        try:
            r = session.get(url, timeout=3)
            break
        except:
            loggererror.error('there is an error on {}'.format(url))
            count = count + 1
            if count == 3:
                break
    if count != 3:
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
        if len(rr) == 0:
            return str(rr)
        index = -1
        advertise = "最快更新，无弹窗"
        adverti = "推荐一款免费小说App"
        advert = "天才壹秒記住"
        if len(rr) > 3:
            for item in rr[-3:]:
                if advertise in item or adverti in item:
                    index = rr.index(item)
                    break
            rr = rr[0: index]
            if advert in rr[0] or 'readx()' in rr[0]:
                rr = rr[1:]
            if "热门推荐" in rr[0]:
                rr = rr[1:]
        else:
            return str(rr)
        return str(rr)
    else:
        return "can not connect"


def deal_ines(itemb, book, index_name):
    res_list = parse_biquge(itemb[1])
    i = 1
    for item in res_list:
        data = {}
        url = itemb[1] + item[1]
        body = {
            "query": {
                "match": {
                    "link": md5(url.encode('utf-8')).hexdigest()
                }
            },
            "_source": ["title", "link"]
        }
        result = EsBackends(index_name, "biquge").search_data(body=body)
        if result["hits"]["total"] == 0:
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
            data['title'] = book.title
            data['link'] = md5(url.encode('utf-8')).hexdigest()
            data['date'] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000+0800")
            data['site_name'] = "biquge"
            data['url'] = url
            with session_scope() as session:
                status = session.add(bc)
                logger.info('the status {}'.format(status))
            EsBackends(index_name, "biquge").index_data(data)
            i = i + 1


def insert_nove():
    index_name = "crawled_url"
    books = session1.query(Book).all()
    session1.close()
    for book in books:
        resu = parse_search(search_url.format("biqugecc", book.title))
        if resu:
            for itemb in resu:
                if book.title == itemb[0]:
                    logger.info("the book is find {}".format(book.title))
                    deal_ines(itemb, book, index_name)
        else:
            resu = parse_search(search_url.format("23uscc", book.title))
            if resu:
                for itemb in resu:
                    if book.title == itemb[0]:
                        logger.info("in 23uscc the book is find {}".format(book.title))
                        deal_ines(itemb, book, index_name)


if __name__ == '__main__':
    insert_nove()
