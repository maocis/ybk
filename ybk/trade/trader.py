#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from datetime import datetime, timedelta

from ybk.models import Collection, TradeAccount, User, Position, Transaction
from ybk.lighttrade import Trader

log = logging.getLogger('trade')


def trade_account_all():
    """ 更新全部账户 """
    for ta in TradeAccount.query():
        update_trade_account(ta)


def transfer(trade_account, inout, amount):
    ta = trade_account
    if not ta.money_password:
        return False, '未登录资金密码'
    t = Trader(ta.exchange, ta.login_name, ta.login_password)
    if inout == 'in':
        r = t.money_in(amount, ta.money_password)
    else:
        r = t.money_out(amount, ta.money_password)
    return r, t.last_error


def withdraw(trade_account, order):
    ta = trade_account
    t = Trader(ta.exchange, ta.login_name, ta.login_password)
    r = t.withdraw(order)
    return r, t.last_error


def order(trade_account, type_, symbol, price, quantity):
    ta = trade_account
    t = Trader(ta.exchange, ta.login_name, ta.login_password)
    if type_ == 'buy':
        r = t.buy(symbol, price, quantity)
    else:
        r = t.sell(symbol, price, quantity)
    return r, t.last_error


def quote_detail(trade_account, symbol):
    ta = trade_account
    t = Trader(ta.exchange, ta.login_name, ta.login_password)
    qd = t.quote_detail(symbol)
    ci = t.list_collection(symbol)[0]
    qd['highest'] = ci['highest']
    qd['lowest'] = ci['lowest']
    return qd


def update_trade_account(trade_account):
    ta = trade_account
    log.info('更新账号{}的信息'.format(ta._id))
    if not ta.login_password:
        ta.verified = False
        ta.verify_message = '没有密码不能登录'
    else:
        try:
            t = Trader(ta.exchange, ta.login_name, ta.login_password)
        except KeyError:
            ta.verified = False
            ta.verify_message = '该交易所协议未破解'
        except Exception as e:
            ta.verified = False
            ta.verify_message = str(e)
        else:
            if not t.is_logged_in:
                ta.verified = False
                ta.verify_message = t.last_error
            else:
                ta.verified = True

                # update money
                ta.money = t.money()
                # update position
                position = t.position()
                if position is not None:
                    for p in position:
                        p['name'] = Collection.get_name(
                            ta.exchange, p['symbol']) or ''
                    ta.position = position

                # update orders
                orders = t.orders()
                aggorders = {}
                for o in orders:
                    o['name'] = Collection.get_name(
                        ta.exchange, o['symbol']) or ''
                    st = (o['symbol'], o['type_'])
                    if st not in aggorders:
                        aggorders[st] = o
                    else:
                        # 把成交汇总一下
                        oo = aggorders[st]
                        amount = oo['price'] * oo['quantity'] + \
                            o['price'] * o['quantity']
                        oo['quantity'] += o['quantity']
                        oo['price'] = amount / oo['quantity']

                orders = aggorders.values()

                ta.orders = orders

                # update order_status
                order_status = t.order_status()
                for o in order_status:
                    o['name'] = Collection.get_name(
                        ta.exchange, o['symbol']) or ''
                ta.order_status = order_status

    ta.upsert()
    user = User.query_one({'_id': ta.user})
    accounting(user)


def accounting(user):
    """ 对账号进行自动记账(如果用户已配置) """
    operated_at = datetime.utcnow() + timedelta(hours=8)

    def add_transaction(type_, exchange, symbol, price, quantity):
        t = Transaction({
            'user': user._id,
            'type_': type_,
            'operated_at': operated_at,
            'exchange': exchange,
            'symbol': symbol,
            'price': price,
            'quantity': quantity,
        })
        t.save()
        if not Position.do_op(t):
            t.remove()

    if user.auto_accounting:
        op = Position.user_position(user._id)
        p2pairs = {}
        for ta in TradeAccount.query({'user': user._id}):
            for p in ta.position or []:
                pair = (ta.exchange, p.symbol)
                if pair not in p2pairs:
                    p2pairs[pair] = p
                else:
                    pp = p2pairs[pair]
                    amount = p.average_price * p.quantity + \
                        pp.average_price * pp.quantity
                    p.quantity += pp.quantity
                    p.average_price = amount / p.quantity
                    p2pairs[pair] = p
        p1pairs = {(p1['exchange'], p1['symbol']): p1 for p1 in op}
        # 检查更改项
        for p1 in op:
            pair = p1['exchange'], p1['symbol']
            if pair[0] in ['湖南文交所', '海西文交所', '上海邮币卡',
                           '上海文交所', '中俄邮币卡']:
                continue
            if pair in p2pairs:
                p2 = p2pairs[pair]
                quantity = p2.quantity - p1['quantity']
                if quantity != 0:
                    type_ = 'buy' if quantity > 0 else 'sell'
                    price = abs(p2.price - p1['avg_buy_price'])
                    price = int(price * 100) / 100.
                    add_transaction(
                        type_, pair[0], pair[1], price, abs(quantity))
            else:
                # 按现价计算已卖出
                if p1['quantity'] > 0:
                    price = int(p1['latest_price'] * 100) / 100.
                    add_transaction(
                        'sell', pair[0], pair[1], price, p1['quantity'])
        # 检查新增项
        for pair, p2 in p2pairs.items():
            if pair[0] in ['湖南文交所', '海西文交所', '上海邮币卡',
                           '上海文交所', '中俄邮币卡']:
                continue
            if pair not in p1pairs and p2.quantity > 0:
                price = int(p2.average_price * 100) / 100.
                add_transaction('buy', pair[0], pair[1], price, p2.quantity)
