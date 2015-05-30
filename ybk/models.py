#!/usr/bin/env python
# -*- coding: utf-8 -*-
from ybk.mangaa import (
    Model,
    IntField,
    FloatField,
    StringField,
    DateTimeField,
)


class Exchange(Model):
    """ 交易所 """
    meta = {
        'idformat': '{abbr}',
        'unique': ['abbr'],
    }

    name = StringField()
    abbr = StringField() # 简称
    url = StringField()
    updated_at = DateTimeField(auto='modified')


class Announcement(Model):
    """ 公告信息 """
    meta = {
        'idformat': '{url}',
        'unique': ['url'],
        'indexes': [
            [[('published_at', 1), ('type_', 1)], {}],
        ],
    }
    exchange = StringField()        # 交易所简称(ID)
    type_ = StringField()           # 申购("offer")/中签("result")
    url = StringField()             # 公告链接
    title = StringField()           # 公告标题
    html = StringField()            # 原始html
    published_at = DateTimeField()  # 交易所发布时间
    updated_at = DateTimeField(auto='modified')


class Offer(Model):
    """ 申购信息

    - 需要解析
    - 有些是图片解析
    """
    meta = {
        'idformat': '{exchange}_{code}',
        'unique': ['exchange', 'code'],
    }

    exchange = StringField()        # 交易所ID(简称)

    code = StringField()            # 交易代码
    issuer = StringField()          # 发行机构
    texture = StringField()         # 材质
    price_forsale = FloatField()    # 挂牌参考价
    quantity_all = IntField()       # 挂牌总数量
    quantity_forsale = IntField()   # 限售总数

    quantity = IntField()           # 供申购数量
    price = FloatField()            # 申购价格
    quantity_accmax = IntField()    # 单账户最大中签数

    change_min = FloatField()       # 最小价格变动单位
    change_limit_1 = FloatField()   # 首日涨跌幅
    change_limit = FloatField()     # 正常日涨跌幅
    pickup_min = IntField()         # 最小提货量
    trade_limit = FloatField()      # 单笔最大下单量

    starts_at = DateTimeField()     # 申购开始日
    ends_at = DateTimeField()       # 申购截止日
    draws_at = DateTimeField()      # 抽签日
    results_at = DateTimeField()    # 中签公布日
    trades_at = DateTimeField()     # 上市交易日

    amount_omv = FloatField()       # 申购人持仓总市值(Open Market Value)
    amount_cash = FloatField()      # 申购资金
    ratio_omv = FloatField()        # 按市值中签率(万元)
    ratio_cash = FloatField()       # 按资金中签率(万元)

    updated_at = DateTimeField(auto='modifield')
