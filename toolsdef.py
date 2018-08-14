# -*- coding: utf-8 -*-
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import loggererror as logger
import time
from utils.session_create import create_session
from bs4 import BeautifulSoup
mysql_client = create_engine(
    "mysql+pymysql://zww:msbasic31@" "192.168.188.114:3306/bailu?charset=utf8",
    encoding="utf-8",
)
from utils.sqlbackends import session_scope
from utils.models import Bookcategory, Book
from tools.bookapi import category, _cate
from utils.es_backends import EsBackends

session_sql = sessionmaker(bind=mysql_client)


@contextmanager
def session_sc():
    session = session_sql()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(e)
        raise
    finally:
        session.close()


def dump_table():
    with session_scope() as session:
        with session_sc() as session1:
            ss = session1.query(Bookcategory).all()
            for s1 in ss:
                d = Bookcategory(
                    id=None,
                    category_name=s1.category_name,
                    male_female=s1.male_female,
                    sort=s1.sort,
                    time_created=s1.time_created,
                    status=s1.status,
                    cover=s1.cover,
                )
                session.add(d)


def cate_table():
    with session_scope() as session:
        i = 1
        for items in category(_cate):
            if items[1]:
                for item in items[1]:
                    b = Bookcategory(id=None, category_major=item[0], category_min=item[1], male_female=items[0],
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


# cate_table()
# index_es()