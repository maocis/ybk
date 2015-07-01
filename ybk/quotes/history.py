import gzip
import struct
from datetime import datetime, timedelta

import requests

from ybk.log import quote_log as log
from ybk.models import Quote, Collection
from ybk.settings import SITES, get_conf

session = requests.Session()
session.headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) ' +
    'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.81 Safari/537.36',
    'Accept-Encoding': 'gzip, deflate, sdch',
}
session.mount('http://',
              requests.adapters.HTTPAdapter(max_retries=5))
session.mount('https://',
              requests.adapters.HTTPAdapter(max_retries=5))


def history_all():
    for site in SITES:
        retries = 3
        while retries > 0:
            retries -= 1
            try:
                history(site)
            except:
                log.exception('站点{}历史行情获取失败, retries={}'.format(site, retries))
            else:
                break


def history(site):
    conf = get_conf(site)
    exchange = conf['abbr']
    url = conf['quote']['history']['url']
    type_ = conf['quote']['history']['type']

    if not url:
        log.warning('{}尚未配置'.format(exchange))
        return

    if type_ == 'sysframe':
        history_sysframe(exchange, url)
    elif type_ == 'winner':
        pass
        log.warning('{}暂时无法解析'.format(exchange))
    else:
        log.warning('{}无法识别'.format(type_))
        return


def history_sysframe(exchange, url):
    for c in Collection.find({'exchange': exchange}):
        try:
            if c.offers_at:
                first_date_before = c.offers_at + timedelta(days=7)
                q = Quote.find_one({'quote_type': '1d',
                                    'quote_at': {'$lte':
                                                 first_date_before}})
                if q:
                    continue
            theurl = '{}/hqApplet/data/day/00{}.day.zip'.format(
                url, c.symbol)
            log.info('fetching exchange {} url {}'.format(exchange, theurl))
            content = session.get(
                theurl, timeout=(5, 10), verify=False).content
            content = gzip.decompress(content)
            num_rows = struct.unpack('>i', content[0:4])[0]
            kline_days = []
            for i in range(num_rows):
                raw_row = content[4 + 40 * i: 4 + 40 * i + 40]
                row = struct.unpack('>i5f2ifi', raw_row)
                t = row[0]
                date = datetime(year=int(str(t)[0:2]) + 1997,
                                month=int(str(t)[2:4]),
                                day=int(str(t)[4:6]),
                                minute=int(str(t)[6:8] or 0),
                                second=int(str(t)[8:10] or 0))
                open_ = row[1]
                high = row[2]
                low = row[3]
                close = row[4]
                mean = row[5]
                # row[6]总是0, 不知道是啥
                volume = row[7]
                amount = row[8]
                quantity = row[9]
                q = {
                    'exchange': exchange,
                    'symbol': c.symbol,
                    'quote_type': '1d',
                    'quote_at': date,
                    'open_': open_,
                    'high': high,
                    'low': low,
                    'mean': mean,
                    'close': close,
                    'volume': volume,
                    'amount': amount,
                }
                if kline_days:
                    q['lclose'] = kline_days[-1]['close']
                else:
                    if not c.offers_at and not c.name.endswith('指数'):
                        c.offers_at = q['quote_at'] - timedelta(days=2)
                        c.offer_price = q['high'] / 1.3
                        c.offer_quantity = quantity // 10
                        log.info('补齐数据:{}_{}, 申购价:{}, 申购量:{}, 时间:{}'
                                 ''.format(c.exchange, c.symbol,
                                           c.offer_price, c.offer_quantity,
                                           c.offers_at))
                        c.save()
                kline_days.append(q)
                Quote(q).upsert()
        except:
            log.exception('{}:{} 抓取失败'.format(c.exchange, c.symbol))
