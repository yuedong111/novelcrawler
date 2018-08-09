# -*- coding: utf-8 -*-


import requests

def create_session():
    s = requests.Session()
    s.headers = {
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/66.0.3359.170 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,"
        "image/webp,image/apng,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4,zh-TW;q=0.2,"
        "ja;q=0.2,ru;q=0.2,gl;q=0.2,ko;q=0.2",
        "Cookie": "ga=GA1.2.1398294235.1533548228;gid=GA1.2.1671757467.1533548228;UM_distinctid=1650ea0ff761f7-0d98196695cc56-182e1503-1fa400-1650ea0ff7830f; CNZZDATA1261698242=274558353-1533547445-http%253A%252F%252Fwww.zhuishushenqi.com%252F%7C1533606794",
    }
    return s