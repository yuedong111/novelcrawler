# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import time
from utils.models import Book, Author, BookCategory
from config import loggerinfo as logger, loggererror
from utils.sqlbackends import session_scope
from utils.session_create import create_session
from tools.bookapi import charpter_api
from toolsdef import cate_url
from utils.es_backends import EsBackends

url_category = "http://www.zhuishushenqi.com/category"
url_rank = "http://www.zhuishushenqi.com/ranking"
url_novel = "http://www.zhuishushenqi.com/book/5816b415b06d1d32157790b1"
url_home = "http://www.zhuishushenqi.com"
url_page = "http://www.zhuishushenqi.com/category?gender={0}&type=hot&major={1}&minor=&page={2}"
api_book = "http://api.zhuishushenqi.com/book/{bookid}"


def parse_novel(url):
    logger.info("the novel url is {}".format(url))
    res = {}
    session = create_session()
    session.encode = "utf-8"
    r = session.get(url)
    soup = BeautifulSoup(r.text, "lxml")
    temp = soup.find("p", {"class": "sup"}).text.split("|")
    if temp[1].strip():
        res["category"] = temp[1]
    else:
        res["category"] = 9
    try:
        total_words = temp[-1]
        if "万字" in total_words:
            total_words = int(total_words[0:-2]) * 10000
        else:
            total_words = total_words[0:-2]
    except:
        total_words = 112212
        loggererror.error("there is an error when deal the totoal words")
        pass
    logger.info("the total words is {}".format(total_words))
    res["total_words"] = total_words
    totals = soup.find_all("i", {"class": "value"})
    if totals:
        totals_hits = totals[0].text.strip()
        likes = totals[1].text.strip()[0:-1]
        total_likes = int(totals_hits) * float(likes) / 100
        res["total_hits"] = totals_hits
        res["total_likes"] = total_likes
    else:
        res["total_hits"] = 0
        res["total_likes"] = 0
    return res


def parse_cate(url):
    logger.info("the url is {}".format(url))
    session = create_session()
    session.encode = "utf-8"
    r = session.get(url)
    soup = BeautifulSoup(r.text, "lxml")
    items = soup.find_all("a", {"class": "book"})
    for item in items:
        title = item.find("img")["alt"].strip()
        author_name = item.find("p", {"class": "author"}).span.text
        category1 = item.find("p", {"class": "author"}).text
        category1.strip().split("|")[1].strip()
        description = item.find("p", {"class": "desc"}).text
        cover = item.find("img")["src"]
        if cover:
            has_cover = 1
        else:
            has_cover = 0
        time_create = int(time.time())
        status = 1
        show_out = 0
        total_presents = 0
        total_presents_amount = 0
        novel_url = item["href"]
        site_book_id = novel_url.split("/")[-1].strip()
        logger.info("bookid {}".format(site_book_id))
        novel_url = url_home + novel_url
        # body = {
        #     "query": {
        #         "bool": {
        #             "must": {
        #                 "match": {"title": title.strip()},
        #                 "match": {"author": author_name.strip()},
        #             }
        #         }
        #     }
        # }
        # search_res = EsBackends("crawled_books", "bookinfo").search_data(body)
        # if search_res["hits"]["total"] == 0 or int(search_res["hits"]["max_score"]) < 8:
        res = parse_novel(novel_url)
        # res1 = charpter_api(api_book.format(bookid=cate))
        with session_scope() as sql_session:
            category_query = (
                sql_session.query(BookCategory)
                .filter_by(category_min=res["category"])
                .first()
            )
            if category_query is None:
                category_query = (
                    sql_session.query(BookCategory)
                    .filter_by(category_major=res["category"])
                    .first()
                )
            book_time = (
                sql_session.query(Book).filter_by(title=title).first()
            )
            author_query = (
                sql_session.query(Author).filter_by(name=author_name).first()
            )
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
            if book_time.time_created:
                b = Book(
                    id=None,
                    author_id=author_id,
                    author_name=author_name,
                    title=title,
                    category_id=category_query.cate_id,
                    status=status,
                    total_words=res["total_words"],
                    total_hits=res["total_hits"],
                    total_likes=res["total_likes"],
                    description=description,
                    has_cover=has_cover,
                    time_created=book_time.time_created,
                    time_updated=time_create,
                    author_remark="",
                    show_out=show_out,
                    vip_chapter_index=25,
                    total_presents=total_presents,
                    total_present_amount=total_presents_amount,
                    sort=0,
                )
                print(' time update')
            else:
                b = Book(
                    id=None,
                    author_id=author_id,
                    author_name=author_name,
                    title=title,
                    category_id=category_query.cate_id,
                    status=status,
                    total_words=res["total_words"],
                    total_hits=res["total_hits"],
                    total_likes=res["total_likes"],
                    description=description,
                    has_cover=has_cover,
                    time_created=time_create,
                    time_updated=time_create,
                    author_remark="",
                    show_out=show_out,
                    vip_chapter_index=25,
                    total_presents=total_presents,
                    total_present_amount=total_presents_amount,
                    sort=0,
                )
            sql_session.add(b)
            # data = {}
            # data["title"] = title.strip()
            # data["author"] = author_name.strip()
            # EsBackends("crawled_books", "bookinfo").index_data(data)
            print("find a book {}".format(title))


def crawler():
    res = cate_url()
    for cate in res.keys():
        for item in res[cate].keys():
            page = 1
            while page < 51:
                url = url_page.format(cate, res[cate][item], page)
                try:
                    parse_cate(url)
                except Exception as e:
                    logger.error(e, exc_info=True)
                    pass
                page = page + 1
                logger.info("now the page is {}".format(page))


# parse_cate(url_category)
# parse_novel(url_novel)
if __name__ == "__main__":
    crawler()
