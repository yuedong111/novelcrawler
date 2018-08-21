# -*- coding: utf-8 -*-

from utils.session_create import create_session
from bs4 import BeautifulSoup

session1 = create_session()


home_url = "http://www.zhuishushenqi.com/selection/bzrt"
def recom():
    r = session1.get(home_url)
    soup = BeautifulSoup(r.text, "lxml")
    temp = soup.find("div", {"class": "c-full-sideBar"}).findChildren()
    for index, d in enumerate(temp):
        if d.name == 'a':
            print(d['href'])


recom()