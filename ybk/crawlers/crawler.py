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
from ybk.settings import SITES, get_conf
import ybk.config

session = requests.Session()
session.headers = {
    'User-Agent': 'Mozilla/5.0',
}


def crawl_all():
    for site in SITES:
        retries = 5
        while retries > 0:
            retries -= 1
            try:
                crawl(site, maxpage=1)
            except:
                log.exception('站点{}爬取失败, retries={}'.format(site, retries))
            else:
                break


def crawl(site, maxpage=None):
    proxy = ybk.config.conf.get('proxy')
    if proxy:
        session.proxies = {'http': proxy}

    conf = get_conf(site)
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
        content = session.get(tconf['index'], timeout=(5, 10)).content
        content = fix_javascript(tconf['index'], content)
        parse_index(ex, type_, content, tconf)
        for page in range(2, maxpage + 1):
            url = tconf['page'].format(page=page)
            content = session.get(url, timeout=(5, 10)).content
            content = fix_javascript(url, content)
            parse_index(ex, type_, content, tconf)


def fix_javascript(url, content):
    """ 中南文交所的幺蛾子

    假定至少安装过node
    """
    import execjs
    try:
        if 'znypjy' in url:
            text = content.decode('gb18030', 'ignore')
            m = re.compile('(function.*?;})window.location').search(text)
            if m:
                script = m.group(1)
                code = execjs.compile(script).call('decoder')
                content = session.get(
                    url + '?' + code, timeout=(5, 10)).content
        elif 'xhcae' in url:
            text = content.decode('gb18030', 'ignore')
            m = re.compile(
                '/notice/\w+/\?WebShieldSessionVerify=\w+').search(text)
            if m:
                url = m.group(0)
                content = session.get(
                    'http://www.xhcae.com' + url, timeout=(5, 10)).content
    except:
        log.exception('')
    return content


def parse_index(ex, type_, content, conf):
    text = content.decode(conf['encoding'], 'ignore')
    for values in re.compile(conf['detail'], re.DOTALL).findall(text):
        d = {key: re.sub(r'(</?[a-zA-Z]+>|\s+)', '', value.strip())
             for key, value in zip(conf['fields'], values)}
        if 'relative' in conf and not d['url'].startswith('http'):
            d['url'] = conf['relative'] + d['url']
        d['published_at'] = parse_datetime(d['published_at']) \
            - timedelta(hours=8)
        d['exchange'] = ex._id
        d['type_'] = type_
        content = session.get(d['url'], timeout=(5, 10)).content
        d['html'] = content.decode(conf['encoding'], 'ignore')
        d['html'] = d['html'].replace(conf['encoding'], 'utf-8')
        log.info('[{exchange}]{published_at}: {title}'.format(**d))
        Announcement(d).upsert()
