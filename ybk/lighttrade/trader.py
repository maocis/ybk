#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import time
import yaml
import logging
import threading

from ybk.lighttrade.sysframe import Client as SysframeClient

log = logging.getLogger('trader')

configfile = open(os.path.join(os.path.dirname(__file__), 'trading.yaml'))
config = yaml.load(configfile)
try:
    accountfile = open(
        os.path.join(os.path.dirname(__file__), 'accounts.yaml'))
    account = yaml.load(accountfile)
except:
    account = {}

lock = threading.RLock()


class Trader(object):

    """ 交易调度 """
    traders = {}

    def __init__(self, exchange, username=None, password=None):
        """ 登陆并缓存Trader Object """
        with lock:
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

            signature = (exchange, username, password)
            if signature not in self.traders:
                if not isinstance(d['tradeweb_url'], list):
                    d['tradeweb_url'] = [d['tradeweb_url']]

                self.client = Client(front_url=d['front_url'],
                                     tradeweb_url=d['tradeweb_url'])
                setattr(self.client, 'exchange', exchange)
                self.client.login(username, password)
                self.traders[signature] = self
            else:
                old = self.traders[signature]
                self.client = old.client
                self.client.keep_alive()

    def __getattr__(self, key):
        if key in self.__dict__:
            return self.__dict__[key]
        else:
            return getattr(self.client, key)

    @property
    def server_time(self):
        t0 = time.time()
        return t0 + self.client.time_offset + self.client.latency * 3

if __name__ == '__main__':
    pass
