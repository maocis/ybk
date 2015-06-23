#!/usr/bin/env python
# -*- coding: utf-8 -*-
import math

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


class Announcement(Model):

    """ 公告信息 """
    meta = {
        'idformat': '{url}',
        'unique': ['url'],
        'indexes': [
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

    from_url = StringField(blank=False)        # 来自哪个公告

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
        cache = getattr(cls, 'cache')
        pair = (exchange, symbol)
        if pair not in cache:
            cache = {(c['exchange'], c['symbol']): c['name']
                     for c in cls.find({},
                                       {'exchange': 1,
                                        'symbol': 1,
                                        'name': 1})}
        return cache.get(pair)

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
