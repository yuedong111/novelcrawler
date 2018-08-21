# -*- coding: utf-8 -*-
from urllib.parse import quote_plus
from time import time
import re
from datetime import datetime
import time
from utils.session_create import create_phone_session
from utils.sqlbackends import session_scope
from utils.models import BookSource
import json
import requests
url_api = "http://api.zhuishushenqi.com/toc?view=summary&book=53f5a98056f543f653a87cb3"
tt=url_cha = "http://api.zhuishushenqi.com/mix-toc/56928442c49f3bce42b7f521"
url_716 = "http://chapter2.zhuishushenqi.com/chapter/http%3A%2F%2Fbook.my716.com%2FgetBooks.aspx%3Fmethod%3Dcontent%26bookId%3D682753%26chapterFile%3DU_682753_201802101656212601_6311_3541.txt?k=4cf909c82ab006b9&t=1534760475"
cc = "http://chapter2.zhuishushenqi.com/chapter/http%3A%2F%2Fbook.my716.com%2FgetBooks.aspx%3Fmethod%3Dcontent%26bookId%3D682753%26chapterFile%3DU_773127_201701231333549899_5019_28.txt?k=d6bbd5ea76086ca7&t=1534761386"
# session = create_phone_session()
# r = session.get(tt)
# temp = r.json()['mixToc']['chapters']
# # tem = json.loads(r.text)
# for item in temp:
#     print(item['title'])

# with session_scope() as ss:
#     dd = ss.query(BookSource).filter_by(book_id=94099).order_by(
#         BookSource.last_site_index.desc()).first()
#
# from book_chap import insert_deal
#
# insert_deal(tt)
import os
url = "http://statics.zhuishushenqi.com/agent/http%3A%2F%2Fimg.1391.com%2Fapi%2Fv1%2Fbookcenter%2Fcover%2F1%2F683291%2F683291_24dfed7fd9b543428149e0afda2a718f.jpg%2F"
os.system('wget {}'.format(url))
