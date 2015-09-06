#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import logging
import lxml.html

log = logging.getLogger('sysframe')


class OfferProtocol(object):

    def list_offer_details(self):
        result = []
        for o in self.list_offers():
            result.append(
                self.offer_detail(o['symbol'], o['price']))
        return result

    def list_offers(self):
        if not self.front_url:
            self.error('front_url未配置')
            return False

        # 为防止意外情况, 每次都网页登陆一下
        self.html_login(module=11)

        url = self.front_url + \
            '/issue_front/issue/subscribeMgr/listSubscribe.action'
        params = {
            'sessionID': self.sid,
            'userID': self.uid,
            'FromModuleID': 18,
            'FromLogonType': 'pc',
            'LogonType': 'pc',
        }
        text = self.session.post(url, params).text
        open('/tmp/text', 'w').write(text)
        t = lxml.html.fromstring(text)
        t = t.xpath('.//div[@class="content"]/table')[0]
        trs = t.xpath('.//tr')
        offers = []
        for tr in trs[2:]:
            tds = tr.xpath('.//td')
            if len(tds) != 7:
                break
            offers.append({
                'symbol': tds[0].text,
                'name': tds[1].text,
                'price': float(tds[2].text),
                'offer_from': tds[3].text,
                'offer_till': tds[4].text,
                'quantity': int(tds[5].text.replace(',', '')),
            })
        return offers

    def offer_detail(self, symbol, price):
        if not self.front_url:
            self.error('front_url未配置')
            return False

        # 为防止意外情况, 每次都网页登陆一下
        self.html_login(module=11)

        url = self.front_url + \
            '/issue_front/issue/subscribeMgr/dealSubscribe.action'
        params = {
            'commodityID_S': symbol,
            'issuePrice': price
        }
        text = self.session.get(url, params=params).text
        t = lxml.html.fromstring(text)
        offer = {
            'name': t.xpath('.//*[@id="commodityName"]')[0].get('value'),
            'symbol': t.xpath('.//*[@id="commodityID"]')[0].get('value'),
            'price': price,
            'quantity': int(t.xpath('.//*[@id="issueQty"]')[0]
                            .get('value').replace(',', '')),
            'min_quantity': int(t.xpath('.//*[@id="minPurchaseQty"]')[0]
                                .get('value').replace(',', '')),
            'max_quantity': int(t.xpath('.//*[@id="maxPurchaseQty"]')[0]
                                .get('value').replace(',', '')),
            'min_change':
                int(t.xpath('.//*[@id="minPurchaseChangeQty"]')
                    [0].get('value')),
            'offer_from': t.xpath('.//*[@id="issueStartDate"]')[0]
            .get('value'),
            'offer_till': t.xpath('.//*[@id="issueStartDate"]')[0]
            .get('value'),
            'can_apply': int(t.xpath('.//*[@id="canBuyQty"]')[0]
                             .get('value').replace(',', '')),
        }
        return offer

    def apply(self, symbol, quantity):
        if not self.front_url:
            self.error('front_url未配置')
            return False

        # 为防止意外情况, 每次都网页登陆一下
        self.html_login(module=11)

        for o in self.list_offers():
            if o['symbol'] == symbol:
                d = self.offer_detail(o['symbol'], o['price'])
                break
        else:
            self.error('申购列表中未找到该品种')
            return False

        url = self.front_url + \
            '/issue_front/issue/subscribeMgr/saveSubscribe.action'

        params = {
            'commodityID': symbol,
            'commodityName': d['name'],
            'issuePrice': d['price'],
            'issueQty': d['quantity'],
            'minPurchaseQty': d['min_quantity'],
            'maxPurchaseQty': d['max_quantity'],
            'minPurchaseChangeQty': d['min_change'],
            'issueStartDate': d['offer_from'],
            'issueEndDate': d['offer_till'],
            'canBuyQty': d['can_apply'],
            'quantity': quantity,
        }

        text = self.session.post(url, params=params).text
        msg = re.compile(r"alert\('([^']+)").search(text).group(1)
        if '成功' in msg:
            return True
        else:
            self.error('申购失败: ' + msg)
            return False

    def apply_status(self):
        if not self.front_url:
            self.error('front_url未配置')
            return False

        # 为防止意外情况, 每次都网页登陆一下
        self.html_login(module=11)

        url = self.front_url + \
            '/issue_front/issue/subscribeMgr/listIssueOrder.action'
        params = {
            'sessionID': self.sid,
            'userID': self.uid,
            'FromModuleID': 18,
            'FromLogonType': 'pc',
            'LogonType': 'pc',
        }
        text = self.session.post(url, params).text
        t = lxml.html.fromstring(text)
        t = t.xpath('.//div[@class="content"]/table')[0]
        trs = t.xpath('.//tr')
        result = []
        for tr in trs[2:-2]:
            tds = tr.xpath('.//td')
            result.append({
                'id': tds[0].text,
                'symbol': tds[1].text,
                'name': tds[2].text,
                'status': tds[3].text,
                'quantity': int(tds[4].text.replace(',', '')),
                'price': float(tds[5].text.replace(',', '')),
                'amount': float(tds[6].text.replace(',', '')),
                'refund': float(tds[7].text.replace(',', '')),
                'commission': float(tds[8].text.replace(',', '')),
                'refund_commission': float(tds[9].text.replace(',', '')),
                'apply_date': tds[10].text,
                'close_date': tds[11].text,
                'sequence_begin': tds[12].text,
                'sequence_end': tds[13].text,
            })
        return result

    def withdraw_apply(self, applyid):
        if not self.front_url:
            self.error('front_url未配置')
            return False

        # 为防止意外情况, 每次都网页登陆一下
        self.html_login(module=11)

        url = self.front_url + \
            '/issue_front/issue/subscribeMgr/orderDel.action'
        params = {'orderNo': applyid}
        self.session.post(url, params=params)
        return True
