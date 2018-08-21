# -*- coding: utf-8 -*-
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import loggererror as logger
import time
from utils.session_create import create_session, create_phone_session
from bs4 import BeautifulSoup
from random import choice
mysql_client = create_engine(
    "mysql+pymysql://zww:msbasic31@" "192.168.188.114:3306/bailu?charset=utf8",
    encoding="utf-8",
)
from utils.sqlbackends import session_scope, session_sql
from utils.models import BookCategory, Book, Author, BookSource, Bookchapter
from tools.bookapi import category, _cate
from utils.es_backends import EsBackends

session_sql1 = sessionmaker(bind=mysql_client)


@contextmanager
def session_sc():
    session1 = session_sql1()
    try:
        yield session1
        session1.commit()
    except Exception as e:
        session1.rollback()
        logger.error(e)
        raise
    finally:
        session1.close()


def dump_table():
    session1 = session_sql1()
    ss = session1.query(BookCategory).all()
    session1.close()
    for s1 in ss:
        d = BookCategory(id=s1.id, category_major=s1.category_major,category_min=s1.category_min,
                         male_female=s1.male_female,sort=s1.sort,time_created=s1.time_created,
                         status=s1.status,cover=s1.status,cate_id=s1.cate_id)
        with session_scope() as session2:
            session2.add(d)


def cate_table():
    with session_scope() as session:
        i = 1
        for items in category(_cate):
            if items[1]:
                for item in items[1]:
                    b = BookCategory(id=None, category_major=item[0], category_min=item[1], male_female=items[0],
                                     sort=i,
                                     time_created=round(time.time()),
                                     status=1, cover='')
                    i = i + 1
                    session.add(b)
            # else:
            #     b = Bookcategory(id=None, category_major=items, male_female=items[0], sort=i,
            #                      time_created=round(time.time()),
            #                      status=1, cover='')
            #     i = i + 1
            #     session.add(b)


def index_es():
    with session_scope() as session:
        books = session.query(Book).all()
        for book in books:
            data = {}
            data["title"] = book.title
            data["author"] = book.author_name
            EsBackends("crawled_books", "bookinfo").index_data(data)
            print('the {} is insert'.format(book.title))


male = "http://www.zhuishushenqi.com/category?gender=male"
female = "http://www.zhuishushenqi.com/category?gender=female"
press = "http://www.zhuishushenqi.com/category?gender=press"
urls = {
    "male": male,
    "female": female,
    "press": press
}
session = create_session()


def zhuishu_category(url, res):
    temp = {}
    r = session.get(url)
    cate = url.split("=")[-1]
    soup = BeautifulSoup(r.text, 'lxml')
    divs = soup.find('div', {'class': 'sort-cells'})
    a = divs.findChildren()
    for item in a:
        num = item['href'].split('=')[-1]
        temp[item.text] = num
    res[cate] = temp


def cate_url():
    res = {}
    for item in urls:
        zhuishu_category(urls[item], res)
    return res


def api(url):
    session = create_session()
    r = session.get(url)
    return r.json()


def insert_cate(url):
    r = api(url)
    i = 1
    for gene in r.keys():
        if gene != 'ok':
            for cate in r[gene]:
                if cate['mins']:
                    for item in cate['mins']:
                        with session_scope() as sqlsession:
                            bc = BookCategory(id=None, category_major=cate['major'], category_min=item,
                                              male_female=gene, time_created=round(time.time()),
                                              status=1, cover='', sort=i)
                            sqlsession.add(bc)
                            i = i + 1
                else:
                    with session_scope() as sqlsession:
                        bc = BookCategory(id=None, category_major=cate['major'], category_min="",
                                          male_female=gene, time_created=round(time.time()),
                                          status=1, cover='', sort=i)
                        sqlsession.add(bc)
                        i = i + 1


def merge_author():
    for i in range(1, 22176):
        session_t = session_sql()
        author = session_t.query(Author).filter_by(id=i).first()
        session_t.close()
        if author:
            with session_sc() as session1:
                a = session1.query(Author).filter_by(name=author.name).first()
                if a:
                    continue
                else:
                    auth = Author(id=None, name=author.name, user_id=author.user_id, has_avator=author.has_avator,
                                  time_created=author.time_created)
                    session1.add(auth)
                    print('insert an author {}'.format(author.name))


def deal_author():
    for i in range(1, 22176):
        with session_sc() as session1:
            author = session1.query(Author).filter_by(id=i).first()
            if author and '|' in author.name.strip():
                session1.delete(author)
                temp = author.name.strip().split('|')
                author.name = temp[0].strip()
                session1.add(author)
                print(i)


def chinese2digits(chinese_str):
    t = chinese_str
    if t is None or t.strip() == "":
        raise Exception("input error for %s" % chinese_str)
    t = t.strip()
    t = t.replace("百十", "百一十")
    common_used_numerals = {'零': 0, '一': 1, '二': 2, '两': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9,
                            '十': 10, '百': 100, '千': 1000, '万': 10000, '亿': 100000000}
    total = 0
    r = 1
    for i in range(len(t) - 1, -1, -1):
        val = common_used_numerals.get(t[i])
        if val is None:
            raise Exception("%s can not be accepted." % t[i])
        if val >= 10 and i == 0:
            if val > r:
                r = val
                total = total + val
            else:
                r = r * val
        elif val >= 10:
            if val > r:
                r = val
            else:
                r = r * val
        else:
            total = total + r * val
    return total


def rand_int():
    num = "123456789"
    res = ""
    for i in range(9):
        res = res + choice(num)
    return int(res)


def delete_book_id():
    session1 = session_sql()
    books = session1.query(BookSource).filter_by(site_id=9).all()
    session1.close()
    for book in books:
        session2 = session_sql()
        bs = session2.query(Bookchapter).filter_by(book_id=book.book_id).all()
        books = session2.query(Book).filter_by(id=book.book_id).all()
        session2.close()
        for b_chapter in bs:
            if b:
                with session_scope() as session3:
                    session3.delete(b_chapter)
                    print('delete ', b.book_id)
        for book in books:
            if book:
                with session_scope() as session4:
                    session4.delete(book)
                    print('delete book', book.id)



# url_cate2 = "http://api.zhuishushenqi.com/cats/lv2"
# url_api = "http://api.zhuishushenqi.com/toc?view=summary&book=53f5a98056f543f653a87cb3"
# # r = create_phone_session().get(url_api)
# # print(r.text)
# cate_table()
# delete_book_id()
# index_es()
# insert_cate(url_cate2)
# merge_author()
# deal_author()
# dump_table()
# if __name__ == '__main__':
#     index_es
