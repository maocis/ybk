#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import time
import yaml
import logging
from datetime import datetime

from sysframe import Client as SysframeClient

log = logging.getLogger('trader')

configfile = open(os.path.join(os.path.dirname(__file__), 'trading.yaml'))
config = yaml.load(configfile)
accountfile = open(os.path.join(os.path.dirname(__file__), 'accounts.yaml'))
account = yaml.load(accountfile)

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

        self.client = Client(front_url=d['front_url'],
                             tradeweb_url=d['tradeweb_url'])
        self.client.login(username, password)

    @property
    def server_time(self):
        t0 = time.time()
        return t0 + self.client.time_offset + self.client.latency

    def buy_at(self, buys, at=datetime(2015, 8, 11, 9, 30)):
        log.info('预约{}下单 {}'.format(at, buys))
        sleep_time = at.timestamp() - self.server_time
        while sleep_time > self.client.latency * 2 + 0.1:
            log.info('离下单还有{}秒'.format(sleep_time))
            self.client.keep_alive()
            self.client.sync_server_time()
            sleep_time = at.timestamp() - self.server_time
            if sleep_time > 0:
                time.sleep(min(sleep_time, 10))

        idx = 0
        while idx < len(buys):
            symbol = buys[idx]['symbol']
            price = buys[idx]['price']
            quantity = buys[idx]['quantity']
            while True:
                done = self.client.buy(symbol, price, quantity)
                exit(0)
                if done:
                    break
            idx += 1

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    t = Trader(exchange='中港文交所',
               username='0001000000484', password='caibahaha')
    t.buy_at(buys=[
                dict(symbol='100041', price=3.9, quantity=10),
                dict(symbol='100044', price=65, quantity=1),
                dict(symbol='100008', price=72.8, quantity=1),
                dict(symbol='100043', price=13, quantity=1),
                dict(symbol='100042', price=8.84, quantity=1),
             ],
             at=datetime(2015, 8, 11, 9, 30))
