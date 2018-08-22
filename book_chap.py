# -*- coding: utf-8 -*-
from __future__ import print_function
from urllib import quote_plus
from time import time
import re
from datetime import datetime
from hashlib import md5
from utils.session_create import create_phone_session
from utils.models import BookSource, Book, Bookchapter
from utils.sqlbackends import session_sql, session_scope
from utils.es_backends import EsBackends
from config import loggererror, loggerinfo
from sqlalchemy.exc import IntegrityError as Integerror
from pymysql.err import IntegrityError

url_api = "http://chapter2.zhuishushenqi.com/chapter/"
url_cha = "http://api.zhuishushenqi.com/mix-toc/"
phone_session = create_phone_session()


def to_unicode(string):
    ret = ""
    for v in string:
        ret = ret + hex(ord(v)).upper().replace("0X", "\\u")

    return ret


def get_content(url):
    c_u = url_api + quote_plus(url)
    count = 0
    while 1:
        try:
            r = phone_session.get(c_u)
            break
        except Exception as e:
            count = count + 1
            if count == 3:
                loggererror.error("time out {}".format(url))
                raise e
            continue
    try:
        content = r.json()["chapter"]["body"].split("\n")
    except Exception as e:
        loggerinfo.info('the content url is {}'.format(url))
        raise e
    total_words = len(str(content)) - 2
    content = str(content)
    return (total_words, content)


def get_chapter(url):
    r = phone_session.get(url)
    for chapter in r.json()["mixToc"]["chapters"]:
        title = chapter["title"]
        res = get_content(chapter["link"])
        yield (title, res, chapter["link"])


def query_book_source():
    session3 = session_sql()
    book_info = session3.query(BookSource).filter_by(site_id=9).all()
    session3.close()
    for item in book_info:
        yield item


def insert_deal(book_info, url):
    data = {}
    index_name = "crawled_url"
    for item in get_chapter(url):
        title = item[0]
        total_words = item[1][0]
        url1 = item[2]
        body = {
            "query": {"match": {"link": md5(url1.encode("utf-8")).hexdigest()}},
            "_source": ["title", "link"],
        }
        # body = {
        #         "query": {
        #             "bool": {
        #                 "must": {
        #                     "match": {"title": title.strip()},
        #                     "match": {"link": url1},
        #                 }
        #             }
        #         }
        #     }
        result = EsBackends(index_name, "api_url").search_data(body=body)
        if result["hits"]["total"] == 0 or float(result["hits"]["max_score"]) < 8:
            loggerinfo.info('the max score is {}'.format(result["hits"]["max_score"]))
            loggerinfo.info('the chapter is {}'.format(title))
            site_index = re.findall(r"\d+\.?\d*", title)
            if len(site_index) == 0:
                continue
            site_index = site_index[0]
            content = item[1][1]
            with session_scope() as session1:
                b_c = Bookchapter(
                    id=None,
                    book_id=book_info.book_id,
                    title=title,
                    time_created=int(time()),
                    total_words=total_words,
                    content=content,
                    source_site_index=site_index,
                )
                try:
                    session1.query(BookSource).filter(BookSource.book_id==book_info.book_id).update({"last_site_index": site]})
                except IntegrityError:
                    loggererror.error('the duplicate id {}'.format(site_index))
                    continue
                except Integerror:
                    continue
                data['title'] = title
                data['link'] = md5(url1.encode("utf-8")).hexdigest()
                data['date'] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000+0800")
                data['site_name'] = "zhuishushenqi"
                EsBackends(index_name, "api_url").index_data(data)
                book = session1.query(Book).filter_by(id=book_info.book_id).first()
                if book:
                    session1.query(Book).filter(Book.id==book_info.book_id).update({"time_index": 0})



def crawler_chapter():
    for book_info in query_book_source():
        if book_info:
            loggerinfo.info('the book id is {}'.format(book_info.book_id))
            b_sid = book_info.site_bookid
            url = url_cha + b_sid
            try:
                insert_deal(book_info, url)
            except Exception as e:
                loggererror.error('the error {}'.format(url))
                loggererror.error(e)



def gen_iter():
    i = 0
    while True:
        i += 1
        yield i


if __name__ == "__main__":
    crawler_chapter()
