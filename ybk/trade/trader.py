#!/usr/bin/env python
# -*- coding: utf-8 -*-
from ybk.models import Collection
from ybk.lighttrade import Trader


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
                ta.money = t.money()
                position = t.position()
                if position:
                    for p in position:
                        p['name'] = Collection.get_name(
                            ta.exchange, p['symbol']) or ''
                    ta.position = position

    ta.upsert()
