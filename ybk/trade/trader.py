#!/usr/bin/env python
# -*- coding: utf-8 -*-
from ybk.models import Collection
from ybk.lighttrade import Trader


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
                position = t.position() or []
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
