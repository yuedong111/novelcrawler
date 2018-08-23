# -*- coding: utf-8 -*-
import time
from utils.session_create import create_session
from bs4 import BeautifulSoup
from utils.sqlbackends import session_scope
from utils.models import BookSource, ZsPromotionCategory, ZsPromotion, Book, Author
session1 = create_session()


home_url = "http://www.zhuishushenqi.com/selection/bzrt"
home = "http://www.zhuishushenqi.com"
page_url = "?page={}"
example_url = "http://www.zhuishushenqi.com/selection/bzrt?page=1"


def get_page(url):
    r = session1.get(url)
    soup = BeautifulSoup(r.text, "lxml")
    temp = soup.find("span", {"class": "total"}).findChildren()
    for d in temp:
        if d.name == 'span':
            return int(d.text)


def parse_html(url, cate_id, sort1):
    sort = sort1
    r = session1.get(url)
    soup = BeautifulSoup(r.text, "lxml")
    book_url = soup.find_all('a', {"class": "book"})
    for b_u in book_url:
        href = b_u['href'].split('/')[-1]
        name = b_u.find('img', {'class': 'cover'})
        author = b_u.find('p', {'class': 'author'})
        author_name = author.text.strip().split('|')[0].strip()
        cate_name = author.text.strip().split('|')[1]
        desc = b_u.find('p', {'class': 'desc'})
        popula = b_u.find('p', {'class': 'popularity'})
        tem = popula.text.split('|')
        th = tem[0].find('人')
        tl = tem[-1].find('%')
        th = tem[0][0: th]
        if "万" in th:
            th = float(th[0:-1]) * 10000
        tl = tem[-1][0: tl]
        tl = float(tl) / 100
        th = int(th)
        tl = th * tl
        tl = int(tl)
        insert_t(href, cate_id, name, author_name, desc, th, tl, sort)
        sort = sort - 1


def insert_t(unique, cate_id, title, author_name, desc, th, tl, sort):
    description = desc
    total_hits = th
    total_likes = tl
    with session_scope() as sql_session:
        b_s = sql_session.query(BookSource).filter_by(site_bookid=unique).first()

        if b_s:
            bookid = b_s.book_id
            zs = ZsPromotion(id=None, category_id=cate_id, book_id=bookid, time_created=int(time.time()),sort=sort)
            sql_session.add(zs)
        else:
            book_time = (
                sql_session.query(Book)
                    .filter_by(title=title, author_name=author_name)
                    .first()
            )
            author_query = sql_session.query(Author).filter_by(name=author_name).first()
            if author_query:
                author_id = author_query.id
            else:
                a = Author(
                    id=None,
                    user_id=0,
                    name=author_name,
                    has_avator=0,
                    time_created=time_create,
                )
                sql_session.add(a)
                author_query3 = (
                    sql_session.query(Author).filter_by(name=author_name).first()
                )
                author_id = author_query3.id
            if book_time:
                book_site = (
                    sql_session.query(BookSource)
                        .filter_by(book_id=book_time.id)
                        .first()
                )
                if book_site and book_site.site_id == 9:
                    sql_session.query(Book).filter(Book.id == book_time.id).update(
                        {"time_updated": time.time(),
                         }
                    )

            else:
                b = Book(
                    id=None,
                    author_id=author_id,
                    author_name=author_name,
                    title=title,
                    category_id=category_query.category_id,
                    status=0,
                    total_words=0,
                    total_hits=total_hits,
                    total_likes=total_likes,
                    description=description,
                    has_cover=0,
                    time_created=time.time(),
                    time_updated=time.time(),
                    author_remark="",
                    show_out=0,
                    vip_chapter_index=25,
                    total_presents=0,
                    total_present_amount=0,
                    sort=0,
                    time_index=0,
                )
                sql_session.add(b)
                print(u"insert a item", b.title)
                book_q = (
                    sql_session.query(Book)
                        .filter_by(title=title, author_id=author_id)
                        .first()
                )
                bs_query = (
                    sql_session.query(BookSource).filter_by(book_id=book_q.id).first()
                )
                if bs_query is None:
                    sitebookid = rand_int()
                    sitebookidext = rand_int()
                    b_s = BookSource(
                        book_id=book_q.id,
                        site_id=9,
                        site_bookid=site_book_id,
                        site_book_id=sitebookid,
                        site_book_id_ext=sitebookidext,
                        last_crawl_time=time_create,
                        status=1,
                        last_site_index=0,
                    )
                    # temp1 = b_s
                    # with session_scope() as session6:
                    #     session6.add(temp1)
                    sql_session.add(b_s)



def recom():
    r = session1.get(home_url)
    soup = BeautifulSoup(r.text, "lxml")
    temp = soup.find("div", {"class": "c-full-sideBar"}).findChildren()
    res = {}
    count = 1
    for index, d in enumerate(temp):
        if d.name == 'a':
            url = home + d['href']
            cate = url.split('/')[-1]
            res[cate] = count
            count = count + 1
    for index, d in enumerate(temp):
        if d.name == 'a':
            url = home + d['href']
            cate = url.split('/')[-1]
            cate_id = res[cate]
            pages = get_page(url)
            total = pages * 20
            url = url + page_url
            i = 1
            while pages >= i:
                parse_html(url.format(i), cate_id, total)
                i = i + 1
                total = total - 20





parse_html(example_url,1,1)

# recom()