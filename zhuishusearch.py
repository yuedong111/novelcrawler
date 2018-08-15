# -*- coding: utf-8 -*-
from utils.session_create import create_session
from bs4 import BeautifulSoup
from zhuishu import parse_novel
import time
from utils.models import Book, Author
from utils.sqlbackends import session_scope
from utils.es_backends import EsBackends
from biquge import session1
session = create_session()

search_url = "http://www.zhuishushenqi.com/search?val={}"


def search_book(url):
    r = session.get(url)
    soup = BeautifulSoup(r.text, 'lxml')
    books = soup.find_all('div', {'class': 'book'})
    if books:
        for book in books:
            t = book.find('h4', {'class': 'name'})
            title = t.text.strip()
            href = t.findChildren()[0]
            link = href['href']
            cate = link.split('/')[-1]
            author_name = book.find('p', {"class": 'author'}).text.strip().split("|")[0].strip()
            description = book.find('p', {'class': 'desc'}).text
            book_url = "http://www.zhuishushenqi.com" + link
            body = {
                "query": {
                    "bool": {
                        "must": {
                            "match": {"title": title.strip()},
                            "match": {"author": author_name.strip()},
                        }
                    }
                }
            }
            search_res = EsBackends("crawled_books", "bookinfo").search_data(body)
            if search_res["hits"]["total"] == 0 or int(search_res["hits"]["max_score"]) < 8:
                res = parse_novel(book_url)
                with session_scope() as sql_session:
                    author_query = (
                        sql_session.query(Book).filter_by(author_name=author_name).first()
                    )
                    author_query2 = (
                        sql_session.query(Author).filter_by(name=author_name).first()
                    )
                    if len(author_name) > 45:
                        author_name = author_name[0:45]
                    if author_query2:
                        author_id = author_query2.id
                    else:
                        a = Author(
                            id=None,
                            user_id=0,
                            name=author_name,
                            has_avator=0,
                            time_created=int(time.time()),
                        )
                        sql_session.add(a)
                        author_query3 = (
                            sql_session.query(Author).filter_by(name=author_name).first()
                        )
                        author_id = author_query3.id
                    b = Book(
                        id=None,
                        author_id=author_id,
                        author_name=author_name,
                        title=title,
                        category_id=1,
                        status=1,
                        total_words=res["total_words"],
                        total_hits=res["total_hits"],
                        total_likes=res["total_likes"],
                        description=description,
                        has_cover=1,
                        time_created=int(time.time()),
                        author_remark="",
                        show_out=1,
                        vip_chapter_index=25,
                        total_presents=0,
                        total_present_amount=0,
                        sort=0,
                        time_index=int(time.time()),
                        site_book_id=cate,
                    )
                    sql_session.add(b)
                    data = {}
                    data["title"] = title.strip()
                    data["author"] = author_name.strip()
                    EsBackends("crawled_books", "bookinfo").index_data(data)
                    print("find a book {}".format(title))


def search():
    i = 1
    while 1:
        book = session1.query(Book).filter_by(id=i).first()
        session1.close()
        if book:
            search_book(search_url.format(book.title))
        else:
            break
        if i % 30 == 0:
            print('i={}'.format(i))
        i = i + 1


if __name__ == '__main__':
    search()