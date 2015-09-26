#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
# from datetime import timedelta, datetime

from yamo import (
    Connection,
    EmbeddedDocument, Document, IDFormatter, Index,
    StringField,
    IntField,
    ListField,
    FloatField,
    BooleanField,
    EmbeddedField,
    DateTimeField,
)


log = logging.getLogger('qd')

exchanges = [
    # '三点零',
    # '上海文交所',
    # '上海邮币卡',
    '东北商交所',
    # '中俄邮币卡',
    '中南文交所',
    '中港邮币卡',
    # '中狮邮币卡',
    '中艺邮币卡',
    '中艺金属所',
    '中融邮币卡',
    # '九州邮币卡',
    # '保利邮币卡',
    # '北京邮交所',
    '北酒所',
    '华东林业所',
    '华中文交所',
    '华夏文交所',
    '华强文交所',
    '南京文交所',
    '南方文交所',
    '南昌文交所',
    '国版老酒所',
    # '天津邮币卡',
    '宁夏文交所',
    '广州文交所',
    '成都文交所',
    # '汉唐邮币卡',
    '江苏文交所',
    # '河北邮币卡',
    # '海西文交所',
    # '湖南文交所',
    '福丽特',
    # '聚奇邮币卡',
    # '西部文交所',
    # '赵湧牛',
    # '重庆文交所',
    # '金陵文交所',
    '金马甲',
    # '阿特多多',
    '青西文交所',
    # '黄金屋'
]


class User(Document):

    """ 抢单用户 """
    class Meta:
        idf = IDFormatter('{mobile}')
        idx1 = Index('mobile', unique=True)
        idx2 = Index('username')

    mobile = StringField(required=True)
    username = StringField(required=True)
    password = StringField(required=True)
    owning = FloatField(default=0)  # 欠款
    paid = FloatField(default=0)  # 已结清

    _is_admin = BooleanField()

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


class Collection(Document):
    exchange = StringField(required=True)
    symbol = StringField(required=True)
    name = StringField(required=True)
    trade_day = IntField(required=True)  # 现在是开始交易的第几个交易日?
    average_price = FloatField(default=0, required=True)  # 平均买入价
    total_quantity = IntField(default=0, required=True)  # 总持有数量
    accounts = ListField(StringField)  # 持有这个品种的账号
    users = ListField(StringField)  # 持有这个品种的用户
    updated_at = DateTimeField(modified=True)


class Account(Document):

    """ 抢单用户的账号 """
    class Meta:
        idf = IDFormatter('{user}_{exchange}_{login_name}')

    user = StringField(required=True)
    exchange = StringField(required=True)
    login_name = StringField(required=True)
    login_password = StringField(required=True)
    money_password = StringField()
    bank_password = StringField()

    @property
    def mobile(self):
        user = User.cached(60).query_one({'_id': self.user})
        return user.mobile

    @property
    def username(self):
        user = User.cached(60).query_one({'_id': self.user})
        return user.username


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


class DailyTrading(Document):

    """ 当日账号汇总 """

    class Meta:
        idf = IDFormatter('{account}_{date}')
        idx1 = Index(['account', 'date'], unique=True)

    date = DateTimeField(required=True)
    account = StringField(required=True)
    position = EmbeddedField(MyPosition)
    orders = EmbeddedField(MyOrder)
    order_status = EmbeddedField(MyStatus)


class Summary(Document):

    """ 各种组合的汇总信息

    总资金/总持仓/总浮盈
    """
    class Meta:
        idf = IDFormatter('{exchange}_{user}_{collection}')
        idx1 = Index('exchange')
        idx2 = Index('user')
        idx3 = Index('collection')

    exchange = StringField(default='', required=True)
    user = StringField(default='', required=True)
    collection = StringField(default='', required=True)

    total_money = FloatField()
    total_capital = FloatField()
    total_profit = FloatField()


conn = Connection('mongodb://localhost/qd')
for d in [User, Collection, Account, DailyTrading, Summary]:
    conn.register(d)
