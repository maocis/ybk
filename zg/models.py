#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
# from datetime import timedelta, datetime

from yamo import (
    Connection,
    EmbeddedDocument, Document, IDFormatter, Index,
    StringField,
    IntField,
    FloatField,
    DateTimeField,
    EmbeddedField,
)

conn = Connection('mongodb://localhost/zg')

log = logging.getLogger('zg')


class User(Document):

    """ 抢单用户 """
    class Meta:
        idf = IDFormatter('{username}')
        idx1 = Index('username', unique=True)

    username = StringField(required=True)
    password = StringField(required=True)


class Account(Document):

    """ 抢单用户的账号 """
    class Meta:
        idf = IDFormatter('{username}_{login_name}')

    username = StringField(required=True)
    login_name = StringField(required=True)
    login_password = StringField(required=True)


class MyPosition(EmbeddedDocument):

    """ 持仓汇总 """

    name = StringField(required=True)
    symbol = StringField(required=True)
    average_price = FloatField(required=True)
    quantity = IntField(required=True)
    price = FloatField(required=True)
    sellable = IntField()
    profit = FloatField()


class MyOrder(EmbeddedDocument):

    """ 成交订单汇总 """

    type_ = StringField(required=True)
    name = StringField(required=True)
    symbol = StringField(required=True)
    price = FloatField(required=True)
    current_price = FloatField(required=True)
    quantity = IntField(required=True)
    commision = FloatField(required=True)
    profit = FloatField(required=True)


class Position(Document):

    """ 当日持仓汇总 """

    class Meta:
        idf = IDFormatter('{username}_{date}')
        idx1 = Index(['username', 'date'], unique=True)

    username = StringField(required=True)
    account_id = StringField(required=True)
    date = DateTimeField(required=True)
    position_list = EmbeddedField(MyPosition)


class Order(Document):

    """ 当日订单汇总 """

    class Meta:
        idf = IDFormatter('{username}_{date}')
        idx1 = Index(['username', 'date'], unique=True)

    username = StringField(required=True)
    account_id = StringField(required=True)
    date = DateTimeField(required=True)
    order_list = EmbeddedField(MyPosition)
