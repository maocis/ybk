#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import pathlib
from datetime import timedelta

import yaml
import requests
from dateutil.parser import parse as parse_datetime

from ybk.models import Exchange, Announcement
from ybk.log import crawl_log as log

from .const import SITES

session = requests.Session()
session.headers = {
    'User-Agent': 'Mozilla 5.0',
}


def crawl_all():
    for site in SITES:
        try:
            crawl(site, maxpage=1)
        except:
            log.exception('')


def crawl(site, maxpage=None):
    cpath = pathlib.Path(__file__).parent / (site + '.yaml')
    conf = yaml.load(cpath.open())
    ex = Exchange({
        'name': conf['name'],
        'url': conf['url'],
        'abbr': conf['abbr'],
    })
    ex.upsert()
    for type_ in ['offer', 'result']:
        tconf = conf[type_]
        if maxpage is None:
            maxpage = tconf['maxpage']
        else:
            maxpage = min(maxpage, tconf['maxpage'])
        content = session.get(tconf['index'], timeout=(3, 7)).content
        parse_index(ex, type_, content, tconf)
        for page in range(2, maxpage + 1):
            url = tconf['page'].format(page=page)
            content = requests.get(url, timeout=(3, 7)).content
            parse_index(ex, type_, content, tconf)


def parse_index(ex, type_, content, conf):
    text = content.decode(conf['encoding'], 'ignore')
    for values in re.compile(conf['detail'], re.DOTALL).findall(text):
        d = {key: re.sub(r'</?[a-zA-Z]+>', '', value.strip())
             for key, value in zip(conf['fields'], values)}
        if 'relative' in conf and not d['url'].startswith('http'):
            d['url'] = conf['relative'] + d['url']
        d['published_at'] = parse_datetime(d['published_at']) \
            - timedelta(hours=8)
        d['exchange'] = ex._id
        d['type_'] = type_
        content = session.get(d['url'], timeout=(3, 7)).content
        d['html'] = content.decode(conf['encoding'], 'ignore')
        d['html'] = d['html'].replace(conf['encoding'], 'utf-8')
        log.info('[{exchange}]{published_at}: {title}'.format(**d))
        Announcement(d).upsert()
