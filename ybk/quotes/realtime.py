#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import json
from datetime import datetime, timedelta

import requests
import lxml.html

from ybk.log import quote_log as log
from ybk.models import Quote, Collection
from ybk.settings import SITES, get_conf

session = requests.Session()
session.headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.81 Safari/537.36',
    'Accept-Encoding': 'gzip, deflate, sdch',
}


def realtime_all():
    for site in SITES:
        retries = 3
        while retries > 0:
            retries -= 1
            try:
                realtime(site)
            except:
                log.exception('站点{}实时行情获取失败, retries={}'.format(site, retries))
            else:
                break


def realtime(site):
    conf = get_conf(site)
    exchange = conf['abbr']
    url = conf['quote']['realtime']['url']
    type_ = conf['quote']['realtime']['type']
    today = datetime.utcnow().replace(
        minute=0, second=0, microsecond=0) + timedelta(hours=8)

    if not url:
        log.warning('{}尚未配置实时行情url'.format(exchange))
        return
    if today.hour < 9 or today.hour > 22:
        log.warning('不在9点到22点之间, 不做解析')
        return

    today = today.replace(hour=0)
    text = session.get(url, timeout=(3, 7)).text
    quotes = parse_quotes(type_, text)
    for q in quotes:
        coll = Collection._get_collection()
        coll.update({'exchange': exchange,
                     'symbol': q['symbol']},
                    {'$set': {'name': q['name']}},
                    upsert=True)
        q['exchange'] = exchange
        q['quote_type'] = '1d'
        q['quote_at'] = today
        if q['open_'] in ['—', '-', None, '']:
            continue
        else:
            Quote(q).upsert()
    log.info('{} 导入 {} 条实时交易记录'.format(exchange, len(quotes)))


def parse_quotes(type_, text):
    if type_ == 'getHqV_lbData':
        # 南京文交所
        rs = json.loads(text)["tables"]
        quotes = [
            {
                'symbol': r['code'],
                'name': r['fullname'],
                'lclose': to_float(r['YesterBalancePrice']),
                'close': to_float(r['CurPrice']),
                'open_': to_float(r['OpenPrice']),
                'low': to_float(r['LowPrice']),
                'high': to_float(r['HighPrice']),
                'volume': to_int(r['TotalAmount']) or 0,
                'amount': to_float(r['TotalMoney']) or 0,
            } for r in rs]
    elif type_ in ['delay_hq', 'display_hq']:
        # 湖南文交所, 上海文交所
        quotes = []
        t = lxml.html.fromstring(text)
        table = t.cssselect('#demo table')[0]
        for tr in table.cssselect('tr'):
            tds = tr.cssselect('td')
            quotes.append({
                'symbol': tds[1].text.strip(),
                'name': tds[2].text.strip(),
                'lclose': to_float(tds[3].text),
                'open_': to_float(tds[4].text),
                'close': to_float(tds[5].text),
                'volume': to_int(tds[7].text),
                'amount': to_float(tds[8].text, multiply=1e4),
                'high': to_float(tds[9].text),
                'low': to_float(tds[10].text),
            })
    elif type_ == 'quotationAction_queryQuotations':
        # 江苏文交所
        rs = json.loads(text)["data"]
        quotes = [
            {
                'symbol': r['goodsId'],
                'name': r['goodsName'],
                'lclose': to_float(r['yclosePrice']),
                'close': to_float(r['newestPrice']),
                'open_': to_float(r['openPrice']),
                'low': to_float(r['minPrice']),
                'high': to_float(r['maxPrice']),
                'volume': to_int(r['totalVolume']),
                'amount': to_float(r['totalCost']),
            } for r in rs]
    elif type_ == 'refreshHQ':
        # 南方文交所
        rs = json.loads(text)["tables"]
        quotes = [
            {
                'symbol': r['c'],
                'name': r['fn'],
                'lclose': to_float(r['ybp']),
                'close': to_float(r['cp']),
                'open_': to_float(r['op']),
                'low': to_float(r['lp']),
                'high': to_float(r['hp']),
                'volume': to_int(r['ta']),
                'amount': to_float(r['tm']),
            } for r in rs]
    elif type_ == 'hqV_lbtc':
        # 福丽特
        quotes = []
        t = lxml.html.fromstring(text)
        table = t.cssselect('table')[0]
        for tr in table.cssselect('tr'):
            tds = tr.cssselect('td')
            quotes.append({
                'symbol': tds[1].text_content().strip(),
                'name': tds[2].text_content().strip(),
                'lclose': to_float(tds[3].text_content()),
                'open_': to_float(tds[4].text_content()),
                'close': to_float(tds[5].text_content()),
                'volume': to_int(tds[7].text_content()),
                'amount': to_float(tds[8].text_content()),
                'high': to_float(tds[9].text_content()),
                'low': to_float(tds[10].text_content()),
            })
    else:
        raise NotImplementedError
    return quotes


def strip_html(s):
    if s:
        return re.sub('(\s+|<[^>]*>)', '', str(s))


def to_float(f, multiply=1.0):
    try:
        return float(strip_html(f)) * multiply
    except:
        return strip_html(f)


def to_int(i):
    try:
        return int(strip_html(i))
    except:
        return strip_html(i)
