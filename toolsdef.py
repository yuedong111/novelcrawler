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
from utils.sqlbackends import session_scope, session_sql
from utils.models import BookCategory, Book, Author
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
    with session_scope() as session:
        with session_sc() as session1:
            ss = session1.query(BookCategory).all()
            for s1 in ss:
                d = BookCategory(
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


url_cate2 = "http://api.zhuishushenqi.com/cats/lv2"

# cate_table()
# index_es()
# insert_cate(url_cate2)
# merge_author()
# deal_author()
if __name__ == '__main__':
    index_es()