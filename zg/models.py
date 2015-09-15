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
    BooleanField,
    ListField,
    EmbeddedField,
    DateTimeField,
)

conn = Connection('mongodb://localhost/zg')

log = logging.getLogger('zg')


class User(Document):

    """ 抢单用户 """
    class Meta:
        idf = IDFormatter('{mobile}')
        idx1 = Index('mobile', unique=True)
        idx2 = Index('username')

    mobile = StringField(required=True)
    username = StringField(required=True)
    password = StringField(required=True)
    paid = FloatField(default=0)
    total_money = FloatField(default=0)
    total_capital = FloatField(default=0)
    total_profit = FloatField(default=0)
    _is_admin = BooleanField(default=False)

    def get_id(self):
        return self._id

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def is_authenticated(self):
        return True

    def is_admin(self):
        return self._is_admin


class Account(Document):

    """ 抢单用户的账号 """
    class Meta:
        idf = IDFormatter('{user_id}_{login_name}')

    user_id = StringField(required=True)
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

    @property
    def increase(self):
        if self.price > 0:
            return '{:4.2f}%'.format(
                (self.price / self.average_price - 1) * 100)
        else:
            return '0%'


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


class MyStatus(EmbeddedDocument):

    """ 挂单情况 """

    order = StringField(required=True)
    order_at = StringField(required=True)
    type_ = StringField(required=True)
    name = StringField(required=True)
    symbol = StringField(required=True)
    price = FloatField(required=True)
    quantity = IntField(required=True)
    pending_quantity = IntField(required=True)
    status = StringField(required=True)


class Position(Document):

    """ 当日持仓汇总 """

    class Meta:
        idf = IDFormatter('{user_id}_{date}')
        idx1 = Index(['user_id', 'date'], unique=True)

    user_id = StringField(required=True)
    date = DateTimeField(required=True)
    position_list = ListField(EmbeddedField(MyPosition))


class Order(Document):

    """ 当日订单汇总 """

    class Meta:
        idf = IDFormatter('{user_id}_{date}')
        idx1 = Index(['user_id', 'date'], unique=True)

    user_id = StringField(required=True)
    date = DateTimeField(required=True)
    order_list = ListField(EmbeddedField(MyOrder))


class Status(Document):

    """ 当日挂单汇总 """

    class Meta:
        idf = IDFormatter('{user_id}_{date}')
        idx1 = Index(['user_id', 'date'], unique=True)

    user_id = StringField(required=True)
    date = DateTimeField(required=True)
    status_list = ListField(EmbeddedField(MyStatus))

conn.register_all()
