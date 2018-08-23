# -*- coding: utf-8 -*-


import requests


def create_session():
    s = requests.Session()
    s.headers = {
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8"
                  "image/webp,image/apng,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "en-US,en;zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4,zh-TW;q=0.2,"
                           "ja;q=0.2,ru;q=0.2,gl;q=0.2,ko;q=0.2",
        "Pragma": "no-cache",
        "Cookie": "_ga=GA1.2.1398294235.1533548228; UM_distinctid=1650ea0ff761f7-0d98196695cc56-182e1503-1fa400-1650ea0ff7830f; _gid=GA1.2.679365455.1534730857; CNZZDATA1261698242=274558353-1533547445-http%253A%252F%252Fwww.zhuishushenqi.com%252F%7C1534920107; _gat=1",
        # "Cookie": "Hm_lvt_534ede4b11a35873e104d2b5040935e0=1533865957; targetEncodingwww23uscom=2; Hm_lpvt_534ede4b11a35873e104d2b5040935e0=1533880072"
    }
    return s


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


USER_AGENTS = (
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0;',
    'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0)',
    'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)',
    'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1) Gecko/20100101 Firefox/4.0.1',
    'Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1',
    'Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; en) Presto/2.8.131 Version/11.11',
    'Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11',
    'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Maxthon 2.0)',
    'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; TencentTraveler 4.0)',
    'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
    'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; The World)',
    'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SE 2.X MetaSr 1.0; SE 2.X MetaSr 1.0; .NET CLR 2.0.50727; SE 2.X MetaSr 1.0)',
    'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; 360SE)',
    'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Avant Browser)',
    'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
    'MQQBrowser/26 Mozilla/5.0 (Linux; U; Android 2.3.7; zh-cn; MB200 Build/GRJ22; CyanogenMod-7) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1',
    'Opera/9.80 (Android 2.3.4; Linux; Opera Mobi/build-1107180945; U; en-GB) Presto/2.8.149 Version/11.10',
)
