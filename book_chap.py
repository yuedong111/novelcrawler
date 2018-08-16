# -*- coding: utf-8 -*-
from urllib.parse import quote_plus
from hashlib import md5
from time import time

from utils.session_create import create_phone_session
from utils.models import BookSource, Book, Bookchapter
from utils.sqlbackends import session_sql, session_scope
from utils.es_backends import EsBackends
from config import loggererror
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
            continue
            if count == 3:
                loggererror.error('time out {}'.format(url))
                raise e
    content = r.json()["chapter"]["body"].split("\n")
    total_words = len(str(content)) - 2
    content = [item.encode('unicode_escape') for item in content]
    content = str(content)
    return (total_words, content)


def get_chapter(url):
    r = phone_session.get(url)
    for chapter in r.json()["mixToc"]["chapters"]:
        title = chapter["title"]
        res = get_content(chapter["link"])
        yield (title, res)


def crawler_chapter(book_id):
    index_name = "crawled_url"
    session_query = session_sql()
    book_info = session_query.query(BookSource).filter_by(id=book_id).first()
    session_query.close()
    if book_info:
        b_sid = book_info.site_book_id
        url = url_cha + b_sid
        body = {
            "query": {"match": {"link": md5(url.encode("utf-8")).hexdigest()}},
            "_source": ["title", "link"],
        }
        result = EsBackends(index_name, "api_url").search_data(body=body)
        if result["hits"]["total"] == 0 or int(result["hits"]["max_score"]) < 8:
            for item in get_chapter(url):
                title = item[0]
                total_words = item[1][0]
                content = item[1][1]
                with session_scope() as session1:
                    session_query1 = session_sql()
                    b = (
                        session_query1.query(Book)
                            .filter_by(title=book_info.title, author_name=book_info.author_name)
                            .first()
                    )
                    b_c = Bookchapter(
                        id=None,
                        book_id=b.id,
                        title=title,
                        time_created=int(time()),
                        total_words=total_words,
                        content=content,
                        source_site_index=2,
                    )
                    session_query1.close()
                    session1.add(b_c)
                    book = session1.query(Book).filter_by(id=b.id).first()
                    if book:
                        session1.delete(book)
                        b = Book(id=book.id, author_id=book.author_id, author_name=book.author_name,
                                 title=book.title,category_id=book.category_id,status=book.status,
                                 total_words=book.total_words,total_hits=book.total_hits,total_likes=book.total_likes,
                                 description=book.description,has_cover=book.has_cover,time_created=book.time_created,
                                 author_remark=book.author_remark,show_out=book.show_out,vip_chapter_index=book.vip_chapter_index,
                                 total_presents=book.total_presents,total_present_amount=book.total_present_amount,sort=book.sort,
                                 time_index=0)
                        session1.add(b)


def gen_iter():
    i = 1
    while True:
        i += 1
        yield i


if __name__ == '__main__':
    for i in gen_iter():
        crawler_chapter(i)