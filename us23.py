# -*- coding: utf-8 -*-
from utils.session_create import create_session
from bs4 import BeautifulSoup


search_url = "https://www.x23us.com/modules/article/search.php"
us23_url = "https://sou.xanbhx.com/search?siteid=23uscc&q={}"
test_url = "https://www.23us.cc/html/324/324121/"
session = create_session()


def dingdian_search(url, data):
    q = {'searchkey': data, 'action': 'login',
         'submit': '', 'searchtype': 'keywords'}

    r = session.post(url, json=q)
    with open('tes.html', 'w') as f:
        print(r.text, file=f)


def us23_chpter(url):
    r = session.get(url)
    soup = BeautifulSoup(r.text, 'lxml')
    tem = soup.find('dl')
    ddt = tem.findChildren()
    chap = ""
    res = list()
    tem = 0
    for index, d in enumerate(ddt):
        if d.name == 'dt' and '最新' not in d.text.strip():
            tem = index
    for d in ddt[tem:]:
        if d.name == "dt":
            chap = d.text.strip()
        if d.name == "dd":
            title = chap + d.text.strip()
            href = d.a["href"]
            res.append((title, href))
    print(res[0:9])
    return res


us23_chpter(test_url)