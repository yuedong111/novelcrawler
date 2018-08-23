# -*- coding: utf-8 -*-
from __future__ import print_function
from bs4 import BeautifulSoup
import time
from utils.models import Book, Author, BookCategory, BookSource, BookCate
from config import loggerinfo as logger, loggererror, loggerimg
from utils.sqlbackends import session_scope, session_sql
from utils.session_create import create_session
from tools.bookapi import charpter_api
from toolsdef import cate_url
from utils.es_backends import EsBackends
from toolsdef import rand_int

url_category = "http://www.zhuishushenqi.com/category"
url_rank = "http://www.zhuishushenqi.com/ranking"
url_novel = "http://www.zhuishushenqi.com/book/5816b415b06d1d32157790b1"
url_home = "http://www.zhuishushenqi.com"
url_page = "http://www.zhuishushenqi.com/category?gender={0}&type=hot&major={1}&minor=&page={2}"
temp_page = "http://www.zhuishushenqi.com/category?gender={0}&type=hot&major={1}"
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
            if total_words == 0:
                total_words = 0
        else:
            total_words = total_words[0:-2]
    except:
        total_words = 0
        # loggererror.error("there is an error when deal the totoal words")
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


def parse_cate(url, total_item, cate_name):
    total_items = total_item
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
        description = item.find("p", {"class": "desc"}).text.strip()
        cover = item.find("img")["src"]
        if cover:
            has_cover = 1
            loggerimg.info(u" |{}|{}|{}".format(cover, title, author_name))
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
                .filter_by(category_name=cate_name)
                .first()
            )
            if category_query is None:
                category_query = BookCategory()
                category_query.category_id = 9
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
                        {"time_updated": time_create, "total_hot": total_items, "category_id": category_query.category_id}
                    )

            else:
                b = Book(
                    id=None,
                    author_id=author_id,
                    author_name=author_name,
                    title=title,
                    category_id=category_query.category_id,
                    status=status,
                    total_words=0,
                    total_hits=res["total_hits"],
                    total_likes=res["total_likes"],
                    description=description,
                    has_cover=0,
                    total_hot= total_items,
                    time_created=time_create,
                    time_updated=time_create,
                    author_remark="",
                    show_out=show_out,
                    vip_chapter_index=25,
                    total_presents=total_presents,
                    total_present_amount=total_presents_amount,
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
                    print("booksource", b_s.book_id)
            print(u"update a book {}".format(title))
        total_items = total_items - 1



def crawler():
    session = create_session()
    res = cate_url()
    for item in res.keys():
        for majar in res[item].keys():
            url = temp_page.format(item, res[item][majar])
            r = session.get(url)
            soup = BeautifulSoup(r.text, 'lxml')
            page1 = soup.find('span', {'class': 'c-gold'})
            pages = int(page1.text)
            page = 1
            total = pages * 20
            if pages > 50:
                pages = 50
            while page < pages+1:
                url = url_page.format(item, res[item][majar], page)
                try:
                    parse_cate(url, total, majar)
                except Exception as e:
                    logger.error(e, exc_info=True)
                    pass
                page = page + 1
                total = total - 20
                logger.info("now the page is {}".format(page))




# parse_cate(url_category)
# parse_novel(url_novel)
if __name__ == "__main__":
    crawler()
