# -*- coding: utf-8 -*-


import requests


def create_session():
    s = requests.Session()
    s.headers = {
        "User-Agent": (
           "ZhuiShuShenQi/3.30.2 (Android 8.0.0; Xiaomi Sagit / Xiaomi MI 6; ????)[preload=false;"
        ),
        "X-User-Agent": "ZhuiShuShenQi/3.30.2 (Android 8.0.0; Xiaomi Sagit / Xiaomi MI 6; ????)[preload=false",
        "X-Device-Id": "f7c8d880d6d74695",
        "Accept-Encoding": "gzip",
        "Connection": "Keep-Alive",
    }
    return s

session = create_session()
r = session.get("http://chapter2.zhuishushenqi.com/chapter/http://book.my716.com/getBooks.aspx?method=content&bookId=2258545&chapterFile=U_2258545_201808142051414307_8896_181.txt")
print(r.text)