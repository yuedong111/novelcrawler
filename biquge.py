# -*- coding: utf-8 -*-
from utils.session_create import create_session
from bs4 import BeautifulSoup


session = create_session()


def parse_biquge(url):
    r = session.get(url)
    soup = BeautifulSoup(r.text, 'lxml')
    item = soup.find('dl')
    ddt = item.findChildren()
    chap = ''
    res = list()
    for d in ddt:
        if d.name == 'dt':
            chap = d.text.strip()
        if d.name == 'dd':
            title = chap + d.text.strip()
            href = d.a['href']
            res.append((title, href))
    return res


def parse_content(url):
    r = session.get(url)
    soup = BeautifulSoup(r.text, 'lxml')
