# -*- coding: utf-8 -*-


import requests

url = "http://chapter2.zhuishushenqi.com/chapter/http%3A%2F%2Fbook.my716.com%2FgetBooks.aspx%3Fmethod%3Dcontent%26bookId%3D2258545%26chapterFile%3DU_2258545_201808142051414307_8896_181.txt?k=8de24280203ccee5&t=1534305460"
url1 = "http://api.zhuishushenqi.com/book/auto-complete?query=圣光下的死亡领主"
url2 = "http://api.zhuishushenqi.com/book/fuzzy-search?query=圣光下的死亡领主"
url3 = "http://api.zhuishushenqi.com/book/59c36d3bea4775d112f1fbf8"
url_cha = "http://api.zhuishushenqi.com/mix-toc/59c36d3bea4775d112f1fbf8"

url_c = "http://chapter2.zhuishushenqi.com/chapter/http%3A%2F%2Fbook.my716.com%2FgetBooks.aspx%3Fmethod%3Dcontent%26bookId%3D2182839%26chapterFile%3DU_2182839_201711171321364413_2904_1.txt"

def create_phone_session():
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


session = create_phone_session()
r = session.get(url_c)
print(r.text)


def to_unicode(string):
    ret = ''
    for v in string:
        ret = ret + hex(ord(v)).upper().replace('0X', '\\u')

    return ret


print(to_unicode("楚风围绕左俊转了一圈，明显感觉他"))