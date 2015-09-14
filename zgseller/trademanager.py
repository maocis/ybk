#!/usr/bin/env python
# -*- coding: utf-8 -*-
import math
import time
import random
import threading
from datetime import datetime
from collections import OrderedDict, Counter
from concurrent.futures import wait, ThreadPoolExecutor

from ybk.lighttrade import Trader

tops = {
    '100010': 539.96,
    '100030': 891.74,
    '100014': 1058.04,
    '100019': 486,
    '100020': 561.66,
    '100028': 76.4,
    '100011': 1114.36,
    '100001': 720,
    '100002': 977.66,
}

names = OrderedDict([
    ('100001', '古代书法'),
    ('100002', '北京饭店'),
    ('100010', '野骆驼'),
    ('100011', '画皮'),
    ('100014', '古代驿站'),
    ('100019', '香港经济建设'),
    ('100020', '彩陶'),
    ('100028', '桃花'),
    ('100030', '豫园'),
])


class TradeManager(object):

    def __init__(self):
        # [(trader, usable), ...]
        self.moneys = []

        # {symbol -> [(trader, quantity), ... ]}
        self.position = {}

        # {symbol -> price}
        self.prices = {}

        # {symbol -> {asks: [], bids: [], ...}}
        self.quotes = {}

        # {symbol -> {buy/sell: quantity, buys/sells: [(username, quantity), ...]}}
        self.pendings = {}

        # {symbol -> price}
        self.highests = {}
        self.lowests = {}

        # [str, ...]
        self.logs = []

        self.traders = [
            Trader('中港邮币卡', '1000000090138', 'caibahaha'),
            Trader('中港邮币卡', '0021000013948', 'caibahaha'),
            Trader('中港邮币卡', '0021000013954', 'caibahaha'),
            Trader('中港邮币卡', '0021000013956', 'caibahaha'),
            Trader('中港邮币卡', '0021000013959', 'caibahaha'),

            Trader('中港邮币卡', '1000000040434', '140718'),
            Trader('中港邮币卡', '1000000090430', '100219'),
            Trader('中港邮币卡', '1000000053321', '100219'),
            Trader('中港邮币卡', '0021000013440', '100219'),
            Trader('中港邮币卡', '0021000013441', '100219'),
            Trader('中港邮币卡', '0021000013439', '100219'),
            Trader('中港邮币卡', '0001000020505', '100219'),
            Trader('中港邮币卡', '0001000020511', '100219'),

            Trader('中港邮币卡', '0002000013882', 'cwf111111'),
            Trader('中港邮币卡', '0002000013890', 'cwf111111'),
            Trader('中港邮币卡', '0002000013903', 'cwf111111'),
            Trader('中港邮币卡', '0002000013916', 'cwf111111'),
            Trader('中港邮币卡', '0002000013924', 'cwf111111'),
            Trader('中港邮币卡', '0002000013931', 'cwf111111'),

            Trader('中港邮币卡', '0021000020181', '27271414q'),

            # Trader('中港邮币卡', '0021000013954', 'caibahaha'),
            # Trader('中港邮币卡', '1000000090430', '100219'),
        ]
        self.investors = [t.investor_info() for t in self.traders]
        self.executor = ThreadPoolExecutor(20)
        self.last_quotes = {}
        self.last_syncs = {}
        self.init_names()

    def init_names(self):
        global names
        for key in names:
            del names[key]
          
        amounts = Counter()
        namedict = {c['symbol']: c['name']
                    for c in self.traders[0].list_collection()}
        for t in self.traders:
            pos = t.position()
            for p in pos or []:
                amounts[p['symbol']]  += p['amount']
        for symbol, amount in amounts.most_common():
            if amount > 10000:
                names[symbol] = namedict[symbol]

    def log(self, msg):
        now = datetime.now()
        hms = now.strftime('%H:%M:%S')
        self.logs.append('[{}] {}'.format(hms, msg))
        self.logs = self.logs[-100:]

    def quote(self, symbol):
        last_quote = self.last_quotes.get(symbol)
        if last_quote and time.time() - last_quote < 0.5:
            time.sleep(random.random() / 2)
         
        t = random.choice(self.traders)
        t.keep_alive()
        quote = t.quote_detail(symbol)
        self.last_quotes[symbol] = time.time()
        return quote

    def sync(self, symbol):
        """ 同步各种数据 """
        last_sync = self.last_syncs.get(symbol)
        if last_sync and time.time() - last_sync < 1:
            return

        ps = []  # (trader, position)
        ms = []  # (trader, usable_money)
        ss = []  # (trader, order_status)

        def keep_alive(t):
            t.keep_alive()

        def sync_position(t):
            ps.append((t, t.position(symbol) or []))

        def sync_money(t):
            ms.append((t, t.money()['usable']))

        def sync_order_status(t):
            ss.append((t, t.order_status(symbol=symbol)))

        def sync_quote(t):
            self.quotes[symbol] = t.quote_detail(symbol)

        def sync_highest_lowest(t):
            c = t.list_collection(symbol)[0]
            self.highests[symbol] = c['highest']
            self.lowests[symbol] = c['lowest']

        futures = []
        for t in self.traders:
            futures.append(self.executor.submit(keep_alive, t))
        wait(futures)

        futures = []
        for t in self.traders:
            futures.append(self.executor.submit(sync_position, t))
            futures.append(self.executor.submit(sync_money, t))
            futures.append(self.executor.submit(sync_order_status, t))
        futures.append(self.executor.submit(sync_quote, self.traders[0]))
        futures.append(self.executor.submit(sync_highest_lowest,
                                            self.traders[-1]))
        wait(futures)

        self.position[symbol] = []
        for t, pos in ps:
            for p in pos:
                if p['symbol'] == symbol:
                    self.prices[symbol] = p['price']
                    self.position[symbol].append((t, p['sellable']))
        self.moneys = ms
        counter = {
            'buy': 0,
            'sell': 0,
            'buys': {},
            'sells': {},
        }
        for t, ol in ss:
            for o in ol:
                if o['status'] in ['ordered', 'partially_done']:
                    type_ = o['type_']
                    tdetail = type_ + 's'
                    counter[type_] += o['pending_quantity']
                    if t.username not in counter[tdetail]:
                        counter[tdetail][t.username] = 0
                    counter[tdetail][t.username] += o['pending_quantity']
        for td in ['buys', 'sells']:
            counter[td] = [(k, v) for k, v in counter[td].items() if v > 0]

        self.pendings[symbol] = counter
        self.last_syncs[symbol] = time.time()

    def get_money(self):
        if not self.moneys:
            return 0
        else:
            return sum(m[1] for m in self.moneys)

    def get_quantity(self, symbol):
        if symbol not in self.position:
            return 0
        else:
            return sum(p[1] for p in self.position[symbol])

    def instant_sell_quantities(self, symbol):
        """ 快卖的数量 """
        total = self.get_quantity(symbol)
        return [total // 512, total // 64, total // 8, total]

    def instant_buy_quantities(self, price):
        total = int(self.get_money() / price)
        return [total // 512, total // 64, total // 8, total]

    def split_sell_quantity(self, symbol, quantity):
        total = self.get_quantity(symbol)
        if total == 0:
            return
        splits = []
        for t, count in self.position[symbol]:
            q = math.ceil(quantity * count / total)
            q = min(q, count)
            splits.append((t, q))
        return splits

    def split_buy_quantity(self, symbol, price, quantity):
        total = self.get_money()
        if total == 0:
            return
        splits = []
        for t, usable in self.moneys:
            q = math.ceil(usable / total * quantity)
            if symbol in self.prices:
                q = min(q, int(usable / price))
            splits.append((t, q))
        return splits

    def order_symbol(self, type_, symbol, price, quantity):
        if quantity <= 0:
            return

        if type_ == 'buy':
            splits = self.split_buy_quantity(symbol, price, quantity)
        elif type_ == 'sell':
            splits = self.split_sell_quantity(symbol, quantity)
        else:
            raise NotImplementedError

        successes = 0
        fails = 0
        errors = []

        def order(t, type_, symbol, price, quantity):
            nonlocal successes, fails
            if type_ == 'buy':
                r = t.buy(symbol, price, quantity)
            else:
                r = t.sell(symbol, price, quantity)
            if r:
                successes += 1
            else:
                fails += 1
                errors.append(t.last_error)

        wait([self.executor.submit(order, t, type_, symbol, price, q)
              for t, q in splits])
        self.log('{} {} {}x{}, 分为{}, {}手成功, {}手失败, 失败原因: {}'
                 ''.format(type_, symbol, price, quantity,
                           [s[1] for s in splits], successes, fails, errors))
        return successes, fails

    def withdraw_symbol(self, symbol, type_='buy'):
        withdrawed_quantity = 0
        failed_quantity = 0
        errors = []

        def withdraw(t):
            nonlocal withdrawed_quantity, failed_quantity
            t.keep_alive()
            for o in t.order_status(symbol=symbol):
                if o['status'] in ['ordered', 'partially_done'] and \
                        o['type_'] == type_ and o['quantity'] > 0:
                    if t.withdraw(o['order']):
                        withdrawed_quantity += o['pending_quantity']
                    else:
                        failed_quantity += o['pending_quantity']
                        errors.append(t.last_error)

        wait([self.executor.submit(withdraw, t)
              for t in self.traders])
        self.log('撤销成功{}手, 失败{}手, 失败原因: {}'
                 ''.format(withdrawed_quantity, failed_quantity, errors))
        return withdrawed_quantity
