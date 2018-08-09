# -*- coding: utf-8 -*-
from utils.session_create import create_session
from bs4 import BeautifulSoup
import time
search_url = 'https://sou.xanbhx.com/search?siteid=biqugecc&q={}'


session = create_session()


def parse_search(url):
    res = {}
    r = session.get(url)
    soup = BeautifulSoup(r.text, 'lxml')
    items = soup.find_all('span', {'class': 's2'})
    for item in items:
        tem = item.find('a')
        if tem:
            res[tem.text.strip()] = tem['href'].strip()
    print(res)








