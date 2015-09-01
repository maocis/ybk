#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import logging
import lxml.html

log = logging.getLogger('sysframe')


class MoneyProtocol(object):

    def html_login(self):
        self.keep_alive()
        self.check_user(module=18, mode='front')
        headers = {
            'x-requested-with': 'XMLHttpRequest',
        }
        url = self.front_url + \
            '/finance_front/checkneedless/communications/sessionGetUser.action'
        params = {
            'sessionID': self.sid,
            'userID': self.uid,
            'FromModuleID': 99,
            'FromLogonType': 'pc',
            'LogonType': 'pc',
        }
        r = self.session.get(url, params=params, headers=headers)
        if r.text != '[true]':
            self.error('综合页面登陆失败, 请检查配置')
            return

        return True

    def money_in(self, amount, password):
        return self.money_transfer("0", amount, password)

    def money_out(self, amount, password):
        return self.money_transfer("1", amount, password)

    def money_transfer(self, type_, amount, password):
        # 为防止意外情况, 每次都网页登陆一下
        self.html_login()

        url = self.front_url + '/bank_front/bank/money/gotoMoneyPage.action'
        params = {
            'sessionID': self.sid,
            'userID': self.uid,
            'FromModuleID': 11,
            'FromLogonType': 'pc',
            'LogonType': 'pc',
        }
        text = self.session.post(url, params).text
        t = lxml.html.fromstring(text)
        bank = t.xpath('.//select[@id="bankID"]/option')[-1].text
        if bank in ['农业银行', '农行', '中国农业银行']:
            if hasattr(self, 'exchange') and self.exchange not in \
                    ['中艺邮币卡', '中艺金属所']:
                self.error('农行需要K宝操作, 无法自动出入金, 中艺所例外')
                return False
        surl = t.xpath('.//form[@id="subfrm"]')[0].get('action')
        params = {
            'inoutMoney': type_,
            'bankID': t.xpath('.//select[@id="bankID"]/option')[-1].get('value'),
            'money': amount,
            'password': password,
            'cardType': t.xpath('.//input[@name="cardType"]')[0].get('value'),
            'inOutStart': '0', # 本行入金
        }
        text = self.session.post(surl, params=params).text
        pat = re.compile("showMsgBox\(1,'([^']+)','([^']+)'")
        t1, t2 = pat.search(text).groups()
        msg = t1 + ':' + t2
        if '成功' in msg:
            log.info('出入金操作返回 {}'.format(msg))
            return True
        else:
            self.error(msg)
