# -*- coding: utf-8 -*-
from utils.session_create import create_session
from urllib.parse import unquote
from itertools import product
url_api = 'http://api.zhuishushenqi.com/mix-atoc/59196481cad7b547270f6e93?view=chapters'
api_book = 'http://api.zhuishushenqi.com/book/{bookid}'
charpter = 'http://chapter2.zhuishushenqi.com/chapter/{link}'

test = 'http://api.zhuishushenqi.com/book/59560cb103f1b121636456b1'
cate_url = 'http://api.zhuishushenqi.com/cats/lv2/statistics'
_cate = 'http://api.zhuishushenqi.com/cats/lv2'


def api(url):
    session = create_session()
    r = session.get(url)
    return r.json()


def charpter_api(url):
    res = {}
    info = api(url)
    res['category'] = info['minorCateV2']
    res['wordCount'] = info['wordCount']
    return res


def category_cover(url):
    res = dict()
    info = api(url)
    cates = info.keys()
    # print(info['picture'])
    for item in cates:
        if item != 'ok':
            for i in info[item]:
                res[i['name'].strip()] = []
                for cover in i['bookCover']:
                    cover_url = cover.split('/')[-1]
                    cover_url = unquote(cover_url)
                    res[i['name']].append(cover_url)
    return res


def category(url):
    info = api(url)
    cates = info.keys()
    res = category_cover(cate_url)
    for item in cates:
        if item != 'ok':
            for i in info[item]:
                temp = product([i['major']],i['mins'])
                # tem = zip(res[i['major'].strip()], temp)
                yield (item,list(temp))


category(_cate)
# category_cover(cate_url)
