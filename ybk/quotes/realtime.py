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
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) ' +
    'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.81 Safari/537.36',
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
    saved = 0
    for q in quotes:
        Collection.update_one({'exchange': exchange,
                               'symbol': q['symbol'].strip()},
                              {'$set': {'name': q['name']}},
                              upsert=True)
        q['exchange'] = exchange
        q['quote_type'] = '1d'
        q['quote_at'] = today
        if q['open_'] in ['—', '-', None, '']:
            continue
        else:
            # 找到上一个交易日的数据, 如果和lclose不符则舍弃
            # 需要保证数据每天更新/不足时需要把日线补足才能正常显示
            lq = Quote.query_one({'exchange': exchange,
                                  'symbol': q['symbol'].strip(),
                                  'quote_type': '1d',
                                  'quote_at': {'$lt': today}},
                                 sort=[('quote_at', -1)])
            if not lq or abs(lq.close - q['lclose']) < 0.01:
                Quote(q).upsert()
                saved += 1

    log.info('{} 导入 {}/{} 条实时交易记录'.format(exchange, saved, len(quotes)))


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
    elif type_ == 'get_hq':
        # 三点零
        quotes = []
        for x in text.splitlines():
            vals = x.split('\t')
            quotes.append({
                'symbol': vals[0].strip(),
                'name': vals[1].strip(),
                'lclose': float(vals[3]),
                'open_': float(vals[4]),
                'high': float(vals[5]),
                'low': float(vals[6]),
                'close': float(vals[7]),
                'volume': int(float(vals[9])),
                'amount': float(vals[34])/100,
            })
    elif type_ == 'req!getsc.action':
        # 华东林业
        quotes = []
        rs = json.loads(text)[0]["ress"]
        for r in rs:
            quotes.append({
                'symbol': r['commodityId'],
                'name': r['fullname'],
                'lclose': float(r['yesterBalancePrice']),
                'open_': float(r['openPrice']),
                'high': float(r['highPrice']),
                'low': float(r['lowPrice']),
                'close': float(r['closePrice']),
                'volume': int(r['totalAmount']),
                'amount': float(r['totalMoney']),
            })
    elif type_ == 'viewStockMarketData.dc':
        # 国版老酒
        quotes = []
        vals = json.loads(text)['values']
        for v in vals:
            quotes.append({
                'symbol': v[1],
                'name': v[2],
                'lclose': float(v[4]),
                'open_': float(v[5]),
                'high': float(v[10]),
                'low': float(v[11]),
                'close': float(v[6]),
                'volume': int(float(v[7])),
                'amount': float(v[8]),
            })
    elif type_ == 'xjsybk':
        # 西部文交所
        quotes = []
        t = lxml.html.fromstring(text)
        trs = t.xpath('.//div[@class="list"]//tr')
        for tr in trs:
            tds = tr.xpath('.//td')
            if len(tds) != 11:
                continue
            quotes.append({
                'symbol': tds[1].text,
                'name': tds[2].text,
                'lclose': float(tds[3].text or 0),
                'open_': float(tds[4].text or 0),
                'close': float(tds[5].text or 0),
                'volume': int(tds[7].text or 0),
                'amount': float(tds[8].text or 0),
                'high': float(tds[9].text or 0),
                'low': float(tds[10].text or 0),
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
