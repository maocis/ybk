#!/usr/bin/env python
# -*- coding: utf-8 -*-
from gevent import monkey; monkey.patch_all()
import gevent.pool

pool = gevent.pool.Pool(50)

import os
import time
import yaml
import logging
from datetime import datetime

from ybk.lighttrade.sysframe import Client as SysframeClient

log = logging.getLogger('trader')

configfile = open(os.path.join(os.path.dirname(__file__), 'trading.yaml'))
config = yaml.load(configfile)
try:
    accountfile = open(os.path.join(os.path.dirname(__file__), 'accounts.yaml'))
    account = yaml.load(accountfile)
except:
    account = {}

class Trader(object):
    """ 交易调度 """
    def __init__(self, exchange, username=None, password=None):
        d = config[exchange]
        if d['system'] == 'sysframe':
            Client = SysframeClient
        elif d['system'] == 'winner':
            raise NotImplementedError

        if username is None:
            u = account[exchange][0]
            username = u['username']
            password = u['password']

        if d.get('disabled'):
            raise ValueError('该交易所被禁止')

        self.client = Client(front_url=d['front_url'],
                             tradeweb_url=d['tradeweb_url'])
        self.client.login(username, password)

    def __getattr__(self, key):
        if key in self.__dict__:
            return self.__dict__[key]
        else:
            return getattr(self.client, key)

    @property
    def server_time(self):
        t0 = time.time()
        return t0 + self.client.time_offset + self.client.latency


    def buy_at(self, symbols, at=datetime(2015, 8, 11, 9, 30)):
        log.info('预约{}下单 {}'.format(at, symbols))
        sleep_time = at.timestamp() - self.server_time
        buys = []
        def update_buys():
            if not buys and sleep_time < 60 * 60:
                for c in self.client.list_collection():
                    if c['symbol'] in symbols:
                        buys.append({'symbol': c['symbol'],
                                     'price': c['highest'],
                                     'quantity': 1})
        update_buys()
        while sleep_time > max(0.5, self.client.latency * 4 + 0.1):
            log.info('离下单还有{}秒'.format(sleep_time))
            update_buys()
            self.client.keep_alive()
            self.client.sync_server_time()
            sleep_time = at.timestamp() - self.server_time
            if sleep_time > 0:
                time.sleep(min(sleep_time - max(0.1, self.client.latency*2),
                               10))
            sleep_time = at.timestamp() - self.server_time

        def do_buy(symbol, price, quantity):
            count = 5
            while count > 0:
                count -= 1
                t0 = time.time()
                done = self.client.buy(symbol, price, quantity)
                t1 = time.time()
                log.info('在{}发送请求,在{}收到回复{}'.format(
                    datetime.fromtimestamp(t0).isoformat(),
                    datetime.fromtimestamp(t1).isoformat(),
                    done))
                if done or '交易时间' not in self.client.last_error:
                    break

        count = 50
        while count > 0:
            for b in buys:
                count -= 1
                pool.spawn(do_buy, b['symbol'], b['price'], b['quantity'])
        pool.join()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
    t = Trader(exchange='广州文交所',
               username='01225133', password='caibahaha')
    t.buy_at(symbols=['602002', '301001'],
             at=datetime(2015, 8, 24, 9, 29, 59, 500000))
