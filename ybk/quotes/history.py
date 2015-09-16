import re
import zlib
import gzip
import struct
import socket
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
                history(site, force=True)
            except:
                log.exception('站点{}历史行情获取失败, retries={}'.format(site, retries))
            else:
                break


def history(site, force=False):
    conf = get_conf(site)
    exchange = conf['abbr']
    url = conf['quote']['history']['url']
    type_ = conf['quote']['history']['type']

    if not url:
        log.warning('{}尚未配置'.format(exchange))
        return

    if type_ == 'sysframe':
        history_sysframe(exchange, url, force)
    elif type_ == 'winner':
        history_winner(exchange, url, force)
    else:
        log.warning('{}无法识别'.format(type_))
        return


def history_sysframe(exchange, url, force):
    for c in Collection.query({'exchange': exchange}):
        try:
            if not force and history_exists(c):
                continue

            # 拿到数据文件
            theurl = ('{}/hqApplet/data/day/00{}.day.zip').format(
                url, c.symbol)
            log.info('fetching exchange {} url {}'.format(exchange, theurl))
            r = session.get(
                theurl, timeout=(5, 10), verify=False)
            if r.status_code != 200:
                log.warning('{}_{}下载失败, 错误码: {}'
                            ''.format(exchange, c.symbol, r.status_code))
                continue
            content = gzip.decompress(r.content)

            # 解析之
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
                # row[6]总是0, 不知道是啥
                q = {
                    'exchange': exchange,
                    'symbol': c.symbol,
                    'quote_type': '1d',
                    'quote_at': date,
                    'open_': row[1],
                    'high': row[2],
                    'low': row[3],
                    'close': row[4],
                    'mean': row[5],
                    'volume': row[7],
                    'amount': row[8],
                    'quantity': row[9],
                }
                if kline_days:
                    q['lclose'] = kline_days[-1]['close']
                    save_quotes(q, c, first_quote=False)
                else:
                    save_quotes(q, c, first_quote=True)
                kline_days.append(q)
        except:
            log.exception('{}:{} 抓取失败'.format(c.exchange, c.symbol))


def history_winner(exchange, url, force):
    assert url.startswith('tcp://')
    host, port = url[6:].split(':')
    port = int(port)
    s = socket.socket()
    s.connect((host, port))

    def get_day_data(symbol):
        bsymbol = symbol.encode('utf-8')
        bizdata = b''.join([
            b'\xfe\x8f\x00\x00', b'\x00' * 12,
            b'\x01\x00',
            b',\x00',
            b'\x02\x04', b'\x00', b'\x00', b'\x00\x00\x00\x00',
            b'\x013' + bsymbol,
            b'\x03\x00', b'\x00\x00',
            b'\x00\x00\x00\x00\x00\x00\x00\x00',
            b'Z\x00\x10\x00\x013' + bsymbol, b'\x00\x00\x00\x00',
            b'\x00', b'\x00',
        ])
        bdata = b''.join([
            b'\x95\x00\x00\x95',
            b'11=524\x00',
            b'13=8\x00',
            b'5=36862\x00',
            b'4=109\x00',
            b'1=66\x008=', bizdata, b'\x00',
            b'1=40\x0069=markid=60ba7308cab942ee961536a74ec7c5f9\x00\x00',
        ])
        s.sendall(bdata)
        batch = 8192
        result = []
        while True:
            result.append(s.recv(batch))
            if len(result[-1]) != batch:
                break
        return b''.join(result)

    def parse_day_data(data):
        size = struct.unpack('>i', b'\x00' + data[1:4])[0]
        assert size + 4 == len(data)
        m = re.compile(b'1=(\d+)\x008=').search(data)
        if m:
            bizsize = int(m.group(1))
            start = m.span()[1]
            try:
                bbiz = zlib.decompress(data[start: start + bizsize])
            except:
                bbiz = data[start: start + bizsize]
            assert bbiz[:4] == b'\xfe\x8f\x00\x00'
            num_packs = struct.unpack('<H', bbiz[16:18])[0]
            sizes = [struct.unpack('<H',
                                   bbiz[18 + 2 * i: 20 + 2 * i])[0]
                     for i in range(num_packs)]

            for i in range(num_packs):
                start = 18 + 2 * num_packs + 0 if i == 0 else sizes[i - 1]
                if bbiz[start:start + 2] == b'\x02\x04':
                    # K线数据
                    symbol = bbiz[start + 10: start + 16].decode('utf-8')
                    count = struct.unpack(
                        '<I', bbiz[start + 16: start + 20])[0]
                    kline_days = []
                    for i in range(count):
                        begin = start + 20 + i * 32
                        row = struct.unpack('<Iiiiiiii',
                                            bbiz[begin: begin + 32])
                        q = {
                            'exchange': exchange,
                            'symbol': symbol,
                            'quote_type': '1d',
                            'quote_at': datetime.strptime(str(row[0]),
                                                          "%Y%m%d"),
                            'open_': row[1] / 100,
                            'high': row[2] / 100,
                            'low': row[3] / 100,
                            'close': row[4] / 100,
                            'amount': row[5] / 1.,
                            'volume': row[6],
                        }
                        if kline_days:
                            q['lclose'] = kline_days[-1]['close']
                            save_quotes(q, c, first_quote=False)
                        else:
                            save_quotes(q, c, first_quote=True)
                        kline_days.append(q)

    for c in Collection.query({'exchange': exchange}):
        try:
            if not force and history_exists(c):
                continue
            if '$' not in c.symbol:
                log.info('feching {}_{} on {}'.format(c.exchange, c.symbol, url))
                data = get_day_data(c.symbol)
                parse_day_data(data)
        except:
            log.exception('{}_{}获取失败'.format(exchange, c.symbol))


def history_exists(c):
    return False
    if c.offers_at:
        first_date_before = c.offers_at + timedelta(days=7)
        q = Quote.query_one({'exchange': c.exchange,
                             'symbol': c.symbol,
                             'quote_type': '1d',
                             'quote_at': {'$lte':
                                          first_date_before}})
        count = Quote.count({'exchange': c.exchange,
                             'symbol': c.symbol,
                             'quote_type': '1d'})

        past_days = (datetime.utcnow() - c.offers_at).days
        if past_days <= 2:
            return True

        trades_ratio = 1. * count / past_days

        if q and trades_ratio > 3 / 7.:
            return True
    return False


def save_quotes(q, c, first_quote=False):
    if first_quote:
        # 看一下需不需要补齐申购数据
        if not c.name.endswith('指数'):
            if not c.offers_at or abs((c.offers_at - q['quote_at']).days) >= 7:
                c.offers_at = q['quote_at'] - timedelta(days=2)
                c.offer_price = q['high'] / 1.3
                if 'quantity' in q:
                    # 假定申购是全部数量的1/10
                    c.offer_quantity = q['quantity'] // 10
                log.info('补齐数据:{}_{}, 申购价:{}, 申购量:{}, 时间:{}'
                         ''.format(c.exchange, c.symbol,
                                   c.offer_price, c.offer_quantity,
                                   c.offers_at))
                # 然而实际上不补齐
                # c.upsert()

    Quote(q).upsert()
