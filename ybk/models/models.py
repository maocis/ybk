#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import math
from itertools import groupby
from collections import defaultdict
from datetime import timedelta, datetime

from ybk.settings import get_conf
from ybk.utils import cached_property_ttl
from .quote import Quote

from .mangaa import (
    Model,
    IntField,
    FloatField,
    StringField,
    BooleanField,
    DateTimeField,
)


class Exchange(Model):

    """ 交易所 """
    meta = {
        'idformat': '{abbr}',
        'unique': ['abbr'],
    }

    name = StringField()
    abbr = StringField()  # 简称
    url = StringField()
    updated_at = DateTimeField(auto='modified')

    @cached_property_ttl(300)
    def num_collections(self):
        """ 交易品种数 """
        return Collection.find({'exchange': self.abbr}).count()

    @cached_property_ttl(300)
    def offers_per_month(self):
        """ 月均申购次数 """
        months = set()
        days = set()
        for c in Collection.cached(300).find({'exchange': self.abbr}):
            if c.offers_at:
                days.add(c.offers_at.strftime('%Y%m%d'))
                months.add(c.offers_at.strftime('%Y%m'))
        if len(days) > 0:
            return len(days) / len(months)

    @cached_property_ttl(300)
    def average_increase(self):
        """ 平均涨幅 """
        result = 0
        count = 0
        for c in Collection.cached(300).find({'exchange': self.abbr}):
            lprice = Quote.latest_price(c.exchange, c.symbol)
            price = c.offer_price
            if lprice and price:
                result += lprice / price - 1
                count += 1
        if count > 0:
            return result / count

    @cached_property_ttl(300)
    def median_increase(self):
        """ 中位数涨幅(半个月-3个月新品) """
        incs = []
        for c in Collection.cached(300).find({'exchange': self.abbr}):
            if offers_between(c, 15, 90):
                lprice = Quote.latest_price(c.exchange, c.symbol)
                price = c.offer_price
                if lprice and price:
                    incs.append(lprice / price - 1)
        if incs:
            return sorted(incs)[len(incs) // 2]

    @cached_property_ttl(300)
    def average_trading_days(self):
        """ 平均上市时间 """
        days = []
        for c in Collection.cached(300).find({'exchange': self.abbr}):
            quotes = Quote.cached(300).find({'exchange': c.exchange,
                                             'symbol': c.symbol,
                                             'quote_type': '1d'})
            days.append(len(quotes))
        if len(days) > 0:
            return sum(days) / len(days)

    def _get_colls_by_day(self):
        colls = Collection.cached(300).find({'exchange': self.abbr})
        colls = [c for c in colls if c.offers_at]
        colls = sorted(colls,
                       key=lambda x: x.offers_at,
                       reverse=False)
        return groupby(colls, lambda x: x.offers_at)

    @cached_property_ttl(300)
    def invest_cash_history(self):
        """ 申购资金历史记录 """
        history = []
        for offers_at, colls in self._get_colls_by_day():
            colls = list(colls)
            invest_cash = sum(c.invest_cash_real or 0
                              for c in colls)
            if invest_cash:
                history.append({
                    'date': colls[0].offers_at,
                    'invest_cash': invest_cash,
                    'total_cash': sum(c.invest_cash_real or 0
                                      for c in Collection.cached(300)
                                      .find({'offers_at': colls[0].offers_at}))
                })
        return history

    @cached_property_ttl(300)
    def offer_cash_history(self):
        """ 申购资金市值历史记录 """
        history = []
        for offers_at, colls in self._get_colls_by_day():
            colls = list(colls)
            offer_cash = sum(c.offer_cash or 0
                             for c in colls)
            if offer_cash:
                history.append({
                    'date': colls[0].offers_at,
                    'offer_cash': offer_cash,
                })
        return history

    @cached_property_ttl(300)
    def result_ratio_history(self):
        """ 中签率历史记录 """
        history = []
        for offers_at, colls in self._get_colls_by_day():
            colls = list(colls)
            total_cash = sum(c.offer_cash or 0
                             for c in colls)
            total_invest = sum(c.invest_cash_real or 0
                               for c in colls)
            if total_invest:
                result_ratio = total_cash / total_invest
                history.append({
                    'date': colls[0].offers_at,
                    'result_ratio': result_ratio,
                })
        return history

    @cached_property_ttl(300)
    def increase_history(self):
        """ 涨幅的历史记录 """
        colls = Collection.cached(300).find({'exchange': self.abbr})

        symbols = [c.symbol for c in colls
                   if offers_between(c, 15, 90)]
        hdict = defaultdict(list)
        for q in Quote.cached(300).find({'exchange': self.abbr,
                                         'symbol': {'$in': symbols},
                                         'quote_type': '1d'},
                                        sort=[('quote_at', 1)]):
            if q.close:
                hdict[q.symbol].append(q.close)
        for symbol, values in hdict.items():
            for i in range(1, len(values)):
                values[i] = values[i] / values[0] * 1.3 - 1
            values[0] = 0.3
        return hdict

    @cached_property_ttl(300)
    def average_result_cash_ratio(self):
        """ 近3次平均中签率 """
        total_invest = 0
        total_offer = 0
        for hi, ho in zip(self.invest_cash_history[-3:],
                          self.offer_cash_history[-3:]):
            total_invest += hi['invest_cash'] or 0
            total_offer += ho['offer_cash'] or 0
        if total_invest > 0 and total_offer > 0:
            return total_offer / total_invest

    @cached_property_ttl(300)
    def average_invest_cash(self):
        """ 平均申购资金 """
        total_invest = 0
        count = 0
        for h in self.invest_cash_history[-3:]:
            total_invest += h['invest_cash'] or 0
            count += 1
        if count > 0 and total_invest > 0:
            return total_invest / 1e8 / count

    @cached_property_ttl(300)
    def expected_invest_cash(self):
        if not self.invest_cash_history:
            return None

        exp = 0
        for i, h in enumerate(reversed(self.invest_cash_history[-3:])):
            exp += 0.7 * (0.3 ** i) * h['invest_cash']
        exp += 0.3 * (0.3 ** i) * h['invest_cash']
        return exp

    @cached_property_ttl(300)
    def rating(self):
        """ 评分 """
        if self.average_result_cash_ratio and self.median_increase:
            return int(self.average_result_cash_ratio *
                       self.median_increase / 0.003)


class Announcement(Model):

    """ 公告信息 """
    meta = {
        'idformat': '{url}',
        'unique': ['url'],
        'indexes': [
            [[('updated_at', 1), ('type_', 1)], {}],
            [[('published_at', 1), ('type_', 1)], {}],
            [[('exchange', 1), ('type_', 1)], {}],
        ],
    }
    exchange = StringField()        # 交易所简称(ID)
    type_ = StringField()           # 申购("offer")/中签("result")
    url = StringField()             # 公告链接
    title = StringField()           # 公告标题
    html = StringField()            # 原始html
    published_at = DateTimeField()  # 交易所发布时间
    updated_at = DateTimeField(auto='modified')

    parsed = BooleanField(default=False)


class Collection(Model):

    """ 收藏品: Stamp/Coin/Card """

    meta = {
        'idformat': '{exchange}_{symbol}',
        'unique': ['exchange', 'symbol'],
        'indexes': [
            [[('exchange', 1), ('symbol', 1)], {}],
            [[('from_url', 1)], {}],
        ]
    }

    from_url = StringField(blank=True)        # 来自哪个公告

    exchange = StringField(blank=False)        # 交易所ID(简称)
    symbol = StringField(blank=False)          # 交易代码
    name = StringField()                        # 交易名
    type_ = StringField(default="邮票")           # "邮票"/"钱币"/"卡片"
    status = StringField(default="申购中")          # "申购中"/"已上市"

    issuer = StringField()          # 发行机构
    texture = StringField()         # 材质
    price_forsale = FloatField()    # 挂牌参考价
    quantity_all = IntField()       # 挂牌总数量
    quantity_forsale = IntField()   # 限售总数

    offer_fee = FloatField(default=0.001)        # 申购手续费
    offer_quantity = IntField()     # 供申购数量 *
    offer_price = FloatField()      # 申购价格 *
    offer_accmax = IntField()       # 单账户最大中签数 *
    offer_overbuy = BooleanField()  # 是否可超额申购 *
    offer_cash_ratio = FloatField()  # 资金配售比例 *

    change_min = FloatField()       # 最小价格变动单位
    change_limit_1 = FloatField()   # 首日涨跌幅
    change_limit = FloatField()     # 正常日涨跌幅
    pickup_min = IntField()         # 最小提货量
    trade_limit = FloatField()      # 单笔最大下单量

    offers_at = DateTimeField(blank=True)     # 申购日 *
    draws_at = DateTimeField(blank=True)      # 抽签日 *
    trades_at = DateTimeField(blank=True)     # 上市交易日 *

    invest_mv = FloatField()       # 申购市值(Market Value)
    invest_cash = FloatField()     # 申购资金 *
    invest_cash_return_ratio = FloatField()   # 资金中签率, 和上面那个二选一 *

    updated_at = DateTimeField(auto='modified')

    @classmethod
    def get_name(cls, exchange, symbol):
        if not hasattr(cls, 'cache'):
            setattr(cls, 'cache', {})
        pair = (exchange, symbol)
        if not cls.cache or cls.cache.get('time', time.time()) < 3600:
            cls.cache = {(c.exchange, c.symbol): c.name
                         for c in cls.find({},
                                           {'exchange': 1,
                                            'symbol': 1,
                                            'name': 1,
                                            '_id': 0})}
            cls.cache['time'] = time.time()
        return cls.cache.get(pair)

    @property
    def offer_mv(self):
        """ 申购市值配额 """
        return self.offer_quantity * self.offer_price * \
            (1 - self.offer_cash_ratio)

    @property
    def offer_cash(self):
        """ 申购资金配额 """
        try:
            return self.offer_quantity * self.offer_price * \
                self.offer_cash_ratio
        except:
            pass

    @property
    def offer_max_invest(self):
        """ 最大申购资金 """
        if self.offer_overbuy:
            return float('inf')
        else:
            return self.offer_mv + \
                self.offer_fee * self.offer_accmax

    @property
    def invest_cash_real(self):
        """ 申购资金(含估算) """
        if self.invest_cash:
            return self.invest_cash
        elif self.invest_cash_return_ratio and self.offer_cash:
            return self.offer_cash / self.invest_cash_return_ratio

    @property
    def result_ratio_cash(self):
        """ 资金中签率 """
        if self.invest_cash_return_ratio:
            return self.invest_cash_return_ratio
        if self.status == "已上市" and self.invest_cash:
            try:
                return self.offer_cash / self.invest_cash
            except:
                pass

    @property
    def result_ratio_mv(self):
        """ 市值中签率 """
        if self.status == "已上市" and self.invest_mv:
            return self.offer_mv * (1 - self.offer_cash_ratio) \
                / self.invest_mv

    @property
    def offer_min_invest(self):
        """ 必中最低申购资金 """
        if self.status == "已上市":
            if self.invest_cash or self.invest_cash_return_ratio:
                magnitude = math.ceil(math.log10(1 / self.result_ratio_cash))
                return self.offer_price * 10 ** magnitude \
                    * (1 + self.offer_fee)

    @property
    def cashout_at(self):
        """ 出金日期 """
        c = get_conf(self.exchange)
        return self.offset(c['cashout'])

    def offset(self, incr):
        c = get_conf(self.exchange)
        notrade = [int(x) for x in str(c['notrade'] or '').split(',') if x]
        delta = 1 if incr > 0 else -1
        odate = self.offers_at
        while incr != 0:
            incr -= delta
            odate += timedelta(days=delta)
            while odate.weekday() in notrade:
                odate += timedelta(days=delta)
        return odate

    @property
    def total_offer_cash(self):
        return sum(c.offer_cash or 0
                   for c in Collection.cached(300)
                   .find({'exchange': self.exchange,
                          'offers_at': self.offers_at}))

    @property
    def expected_invest_cash(self):
        ex = Exchange.find_one({'abbr': self.exchange})
        if ex.expected_invest_cash and self.total_offer_cash:
            return (self.offer_cash or 0) / self.total_offer_cash \
                * ex.expected_invest_cash

    @property
    def expected_annual_profit(self):
        """ 预期年化收益率 """
        ex = Exchange.find_one({'abbr': self.exchange})
        if ex.expected_invest_cash:
            return self.expected_result_cash_ratio * ex.median_increase

    @property
    def expected_result_cash_ratio(self):
        """ 预期资金中签率 """
        if not self.result_ratio_cash:
            ex = Exchange.find_one({'abbr': self.exchange})
            if ex.expected_invest_cash:
                return self.total_offer_cash / ex.expected_invest_cash
        else:
            return self.result_ratio_cash


def offers_between(c, low=15, high=90):
    return c.offers_at and \
        c.offers_at < ndays_ago(low) and \
        c.offers_at > ndays_ago(high)


def ndays_ago(n):
    return datetime.utcnow() - timedelta(days=n)
