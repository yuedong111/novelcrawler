# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import time
from utils.models import Book, Author, Bookid, Bookcategory
from config import logger
from utils.sqlbackends import session_scope
from utils.session_create import create_session
from bookapi import charpter_api

url_category = "http://www.zhuishushenqi.com/category"
url_rank = "http://www.zhuishushenqi.com/ranking"
url_novel = "http://www.zhuishushenqi.com/book/5816b415b06d1d32157790b1"
url_home = "http://www.zhuishushenqi.com"
url_page = (
    "http://www.zhuishushenqi.com/category?gender=male&type=hot&major=1&minor=&page={}"
)
api_book = 'http://api.zhuishushenqi.com/book/{bookid}'


def parse_novel(url):
    logger.info("the novel url is {}".format(url))
    res = {}
    session = create_session()
    session.encode = "utf-8"
    r = session.get(url)
    soup = BeautifulSoup(r.text, "lxml")
    total_words = soup.find("p", {"class": "sup"}).text.split("|")[-1]
    if "万字" in total_words:
        total_words = int(total_words[0:-2]) * 10000
    else:
        total_words = total_words[0:-2]
    logger.info("the total words is {}".format(total_words))
    res["total_words"] = total_words
    totals = soup.find_all("i", {"class": "value"})
    totals_hits = totals[0].text.strip()
    likes = totals[1].text.strip()[0:-1]
    total_likes = int(totals_hits) * float(likes) / 100
    res["total_hits"] = totals_hits
    res["total_likes"] = total_likes
    return res


def parse_cate(url):
    logger.info("the url is {}".format(url))
    session = create_session()
    session.encode = "utf-8"
    r = session.get(url)
    soup = BeautifulSoup(r.text, "lxml")
    items = soup.find_all("a", {"class": "book"})
    for item in items:
        title = item.find("img")["alt"]
        author_name = item.find("p", {"class": "author"}).span.text
        category = item.find("p", {"class": "author"}).text
        category = category.strip().split("|")[1].strip()
        description = item.find("p", {"class": "desc"}).text
        cover = item.find("img")["src"]
        if cover:
            has_cover = 1
        else:
            has_cover = 0
        time_create = int(time.time())
        category_id = 1
        status = 1
        show_out = 1
        total_presents = 0
        total_presents_amount = 0
        novel_url = item["href"]
        cate = novel_url.split('/')[-1].strip()
        logger.info('bookid {}'.format(cate))
        novel_url = url_home + novel_url
        res = parse_novel(novel_url)
        res1 = charpter_api(api_book.format(bookid=cate))
        with session_scope() as sql_session:
            category_query = sql_session.query(Bookcategory).filter_by(category_name=res1['category']).first()
            author_query = (
                sql_session.query(Book).filter_by(author_name=author_name).first()
            )
            author_query2 = (
                sql_session.query(Author).filter_by(name=author_name).first()
            )
            if author_query2:
                author_id = author_query2.id
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

            if author_query:
                b = Book(
                    id=None,
                    author_id=author_id,
                    author_name=author_name,
                    title=title,
                    category_id=category_query.id,
                    status=status,
                    total_words=res["total_words"],
                    total_hits=res["total_hits"],
                    total_likes=res["total_likes"],
                    description=description,
                    has_cover=has_cover,
                    time_created=time_create,
                    author_remark="",
                    show_out=show_out,
                    vip_chapter_index=25,
                    total_presents=total_presents,
                    total_present_amount=total_presents_amount,
                    sort=0,
                    time_index=time_create,
                    site_book_id=cate,
                )
            else:
                b = Book(
                    id=None,
                    author_id=author_id,
                    author_name=author_name,
                    title=title,
                    category_id=category_id,
                    status=status,
                    total_words=res["total_words"],
                    total_hits=res["total_hits"],
                    total_likes=res["total_likes"],
                    description=description,
                    has_cover=has_cover,
                    time_created=time_create,
                    author_remark="",
                    show_out=show_out,
                    vip_chapter_index=25,
                    total_presents=total_presents,
                    total_present_amount=total_presents_amount,
                    sort=0,
                    time_index=time_create,
                    site_book_id=cate,
                )
            sql_session.add(b)


def crawler():
    page = 1
    while page < 51:
        url = url_page.format(page)
        parse_cate(url)
        page = page + 1
        logger.info("now the page is {}".format(page))


# parse_cate(url_category)
# parse_novel(url_novel)
if __name__ == "__main__":
    try:
        crawler()
    except Exception as e:
        logger.error(e, exc_info=True)
