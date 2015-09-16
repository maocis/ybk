#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import time
from datetime import datetime

import requests

announcements = {}

def shorten_url(url, remove_http=True):
    url_short = ''
    try:
        r = requests.post('http://dwz.cn/create.php', data={'url': url},
                          timeout=10)
    except:
        return shorten_url(url, remove_http)
    else:
        j = r.json()
        if j['status'] != 0:
            return shorten_url(url, remove_http)
        else:
            url_short = j['tinyurl']

    if remove_http:
        if url_short.startswith('https://'):
            return url_short[len('https://'):]
        return url_short[len('http://'):]
    return url_short


def send_sms(mobile, text):
    url = 'http://yunpian.com/v1/sms/send.json'
    data = {
        'apikey': 'ffd6760c4875e37e942b117890ef2558',
        'mobile': mobile,
        'text': text,
    }
    r = requests.post(url, data=data).json()
    print(r)
    return r


def get_all_announcements():
    try:
        r = requests.get('http://www.zgyoubi.com/index.php', timeout=(3, 7))
        pat = re.compile('<a href="news_look\.php\?id=(\d+)"[^>]*>([^<]+)</a>')
        return dict(pat.findall(r.content.decode('utf-8', 'ignore')))
    except:
        pass


def send_announcements(ids):
    users = [
        ('13611825698', '胡景超'),
        ('13816992232', '徐驸骅'),
    ]
    for id_ in ids:
        # url = 'http://www.zgyoubi.com/news_look.php?id=' + id_
        title = announcements[id_]
        print('[{}] title={}'.format(datetime.now(), title))
        msg = '【邮币卡369】尊敬的{}, 您关注的公告更新了, 请访问相应地址查看'
        for mobile, name in users:
            try:
                msg = msg.format(name)
                send_sms(mobile, msg)
            except:
                pass


announcements.update(get_all_announcements())
print('[{}] 已有公告: {}'.format(datetime.now(), list(announcements.keys())))

while True:
    na = get_all_announcements()
    new_ids = set(na.keys()) - set(announcements.keys())
    announcements.update(na)
    if new_ids:
        print('[{}] 新公告: {}'.format(datetime.now(), new_ids))
        send_announcements(new_ids)
    else:
        print('[{}] 没有新公告'.format(datetime.now()))
    time.sleep(10)


