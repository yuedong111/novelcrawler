# -*- coding: utf-8 -*-
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Text, Integer, DateTime, Boolean
from sqlalchemy import create_engine
Base = declarative_base()
mysql_client = create_engine(
    "mysql+pymysql://zww:msbasic31@" "192.168.188.114:3306/bailu?charset=utf8",
    encoding="utf-8",
)


class Book(Base):
    __tablename__ = "book"
    id = Column(Integer, autoincrement=True, primary_key=True)
    author_id = Column(Integer, index=True)
    author_name = Column(String(45), index=True)
    title = Column(String(128), index=True)
    category_id = Column(Integer)
    status = Column(Integer)
    total_words = Column(Integer)
    total_hits = Column(Integer)
    total_likes = Column(Integer)
    description = Column(String(2048))
    has_cover = Column(Integer)
    time_created = Column(Integer)
    time_updated = Column(Integer)
    author_remark = Column(String(128))
    show_out = Column(Integer)
    vip_chapter_index = Column(Integer)
    total_presents = Column(Integer)
    total_present_amount = Column(Integer)
    sort = Column(Integer)
    time_index = Column(Integer, index=True)


class Author(Base):
    __tablename__ = "author"
    id = Column(Integer, autoincrement=True, primary_key=True)
    user_id = Column(Integer, index=True)
    name = Column(String(55))
    has_avator = Column(Integer)
    time_created = Column(Integer)


class BookCategory(Base):
    __tablename__ = "book_category_map"
    id = Column(Integer, autoincrement=True, primary_key=True)
    category_major = Column(String(45), comment='大分类')
    category_min = Column(String(45), comment='小分类')
    male_female = Column(String(30))
    sort = Column(Integer)
    time_created = Column(Integer)
    status = Column(Integer)
    cover = Column(String(1025))
    cate_id = Column(Integer)


class BookId(Base):
    __tablename__ = "bood_id"
    id = Column(Integer, autoincrement=True, primary_key=True)
    site_id = Column(Integer)
    site_name = Column(String(20))
    site_book_id = Column(String(32))
    title = Column(String(55))
    author_name = Column(String(55))


class Bookchapter(Base):
    __tablename__ = 'book_chapter'
    id = Column(Integer, autoincrement=True, primary_key=True)
    book_id = Column(Integer, index=True)
    title = Column(String(128))
    time_created = Column(Integer)
    total_words = Column(Integer)
    content = Column(Text(length=(2**32)-1))
    source_site_index = Column(Integer, index=True)


class BookSource(Base):
    __tablename__ = 'book_source_site'
    book_id = Column(Integer, primary_key=True)
    site_id = Column(Integer, primary_key=True)
    site_book_id = Column(Integer)
    site_book_id_ext = Column(Integer)
    last_crawl_time = Column(Integer)
    status = Column(Integer)
    last_site_index = Column(Integer)
    site_bookid = Column(String(32))


# Base.metadata.create_all(mysql_client)