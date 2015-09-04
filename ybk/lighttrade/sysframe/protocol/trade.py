#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging

log = logging.getLogger('sysframe')


class TradeProtocol(object):

    def list_collection(self, symbol=None):
        """ 列表可交易藏品

        :param symbol: 为空时列表全部
        """
        cid = self.mid + str(symbol) if symbol else ''
        d = self.request_tradeweb('commodity_query', {'USER_ID': self.uid,
                                                      'SESSION_ID': self.sid,
                                                      'COMMODITY_ID': cid})
        r = d['GNNT']['REP']
        if r['RESULT']['RETCODE'] == '0':
            recs = r['RESULTLIST']['REC']
            if isinstance(recs, dict):
                recs = [recs]
            log.info('获得{}个可交易藏品信息'.format(len(recs)))
            return [{
                'symbol': rec['CO_I'],
                'name': rec['CO_N'],
                'highest': float(rec['SP_U']),
                'lowest': float(rec['SP_D']),
            } for rec in recs]
        else:
            self.error('列表可交易藏品失败: {}'.format(r['RESULT']['MESSAGE']))

    def money(self):
        """ 可用资金 """
        d = self.request_tradeweb('firm_info', {'USER_ID': self.uid,
                                                'SESSION_ID': self.sid})
        r = d['GNNT']['REP']
        if r['RESULT']['RETCODE'] == '0':
            rec = r['RESULTLIST']['REC']
            log.info('可用资金 {}, 可取资金 {}'.format(rec['UF'], rec['DQ']))
            return {'usable': float(rec['UF']),
                    'withdrawable': float(rec['DQ'])}
        else:
            self.error('可用资金查询失败: {}'.format(r['RESULT']['MESSAGE']))

    def quote_detail(self, symbol):
        """ 盘口数据查询 """
        cid = self.mid + str(symbol)
        d = self.request_tradeweb('commodity_data_query',
                                  {'USER_ID': self.uid,
                                   'COMMODITY_ID': cid,
                                   'SESSION_ID': self.sid})
        r = d['GNNT']['REP']
        if r['RESULT']['RETCODE'] == '0':
            rec = r['RESULTLIST']['REC']
            return {
                'name': rec['CO_N'],
                'price': float(rec['PR_C']),
                'bid': float(rec['BID']),  # 买一价
                'ask': float(rec['OFFER']),  # 卖一价
                'high': float(rec['HIGH']),
                'low': float(rec['LOW']),
                'last': float(rec['LAST']),
                'average': float(rec['AVG']),  # 均价
                'change': float(rec['CHA']),  # 涨跌
                'volume': int(rec['VO_T']),  # 成交量
                'total': int(rec['TT_O']),  # 藏品总量
                'bids': [{'price': float(rec['BP_' + str(i)]),
                          'quantity': int(rec['BV_' + str(i)])}
                         for i in range(1, 6)],
                'asks': [{'price': float(rec['SP_' + str(i)]),
                          'quantity': int(rec['SV_' + str(i)])}
                         for i in range(1, 6)],
            }
        else:
            self.error('盘口数据查询失败: {}'.format(r['RESULT']['MESSAGE']))

    def position(self):
        """ 持仓查询 """
        d = self.request_tradeweb('holding_query', {'USER_ID': self.uid,
                                                    'COMMODITY_ID': '',
                                                    'STARTNUM': 0,
                                                    'RECCNT': 0,
                                                    'SESSION_ID': self.sid,
                                                    'MARKET_ID': ''})
        r = d['GNNT']['REP']
        if r['RESULT']['RETCODE'] == '0':
            total = int(r['RESULT']['TTLREC'])
            if total == 0:
                return []

            recs = r['RESULTLIST']['REC']
            if isinstance(recs, dict):
                recs = [recs]
            pos = [{'symbol': rec['CO_I'][len(self.mid):],
                    'quantity': int(rec['BU_H']),
                    'sellable': int(rec['B_V_H']),
                    'average_price': float(rec['BU_A']),
                    'amount': float(rec['MV']),
                    'profit': float(rec['NP_PF']),
                    'increase': float(rec['LP_R']),
                    }
                   for rec in recs]
            for p in pos:
                p['price'] = p['average_price'] * (1 + p['increase'])
            assert total == len(pos), '还没实现依次取'

            log.info('持有品种{}个, 市值{}元, 收益{}元'
                     ''.format(len(pos),
                               sum(p['amount'] for p in pos),
                               sum(p['profit'] for p in pos)
                               ))
            return pos
        else:
            self.error('持仓查询失败: {}'.format(r['RESULT']['MESSAGE']))

    def order(self, symbol, price, quantity, type_=1):
        """ 下单
        :param type_: 1 为买, 2 为卖
        """
        cid = self.mid + str(symbol)
        price = '{:.2f}'.format(price)
        closemode = '0' if type_ == 1 else '1'
        d = self.request_tradeweb('order', {'USER_ID': self.uid,
                                            'CUSTOMER_ID': self.cid,
                                            'SESSION_ID': self.sid,
                                            'BUY_SELL': type_,
                                            'COMMODITY_ID': cid,
                                            'PRICE': price,
                                            'QTY': str(quantity),
                                            'SETTLE_BASIS': type_,
                                            'CLOSEMODE': closemode,
                                            'TIMEFLAG': '0',
                                            'L_PRICE': '0',
                                            'BILLTYPE': '0'})

        r = d['GNNT']['REP']['RESULT']
        if r['RETCODE'] == '0':
            log.info('下单成功{} {}x{}'.format(symbol, price, quantity))
            return r['OR_N']
        else:
            self.error('下单失败: {}'.format(r['MESSAGE']))
            return False

    def buy(self, *args, **kwargs):
        kwargs['type_'] = 1
        return self.order(*args, **kwargs)

    def sell(self, *args, **kwargs):
        kwargs['type_'] = 2
        return self.order(*args, **kwargs)

    def order_status(self, order=None):
        """ 委托查询 """
        if not order:
            order = 0
        d = self.request_tradeweb('my_weekorder_query',
                                  {'USER_ID': self.uid,
                                   'BUY_SELL': 0,
                                   'ORDER_NO': order,
                                   'COMMODITY_ID': '',
                                   'STARTNUM': 0,
                                   'RECCNT': 0,
                                   'UT': 0,
                                   'SESSION_ID': self.sid,
                                   'MARKET_ID': ''})
        r = d['GNNT']['REP']
        if r['RESULT']['RETCODE'] == '0':
            total = int(r['RESULT'].get('TTLREC', '0'))
            if total == 0:
                return []
            log.info('本周有{}笔委托, 返回最新的{}笔'
                     ''.format(r['RESULT']['TTLREC'],
                               len(r['RESULTLIST']['REC'])))

            recs = r['RESULTLIST']['REC']
            if not isinstance(recs, list):
                recs = [recs]
            return [{'order': rec['OR_N'],
                     'order_at': rec['TIME'],
                     'status': {'1': 'ordered',
                                '2': 'partailly_done',
                                '3': 'all_done',
                                '5': 'all_canceled',
                                '6': 'partially_canceled'}.get(rec['STA']),
                     'type_': {'1': 'buy', '2': 'sell'}.get(rec['TYPE']),
                     'symbol': rec['CO_I'][len(self.mid):],
                     'price': float(rec['PRI']),
                     'quantity': int(rec['QTY']),
                     'pending_quantity': int(rec['BAL']),
                     } for rec in recs]

        else:
            self.error('委托查询失败: {}'.format(r['RESULT']['MESSAGE']))
            return []

    def withdraw(self, order):
        """ 撤单 """
        d = self.request_tradeweb('order_wd', {'USER_ID': self.uid,
                                               'ORDER_NO': order,
                                               'SESSION_ID': self.sid})
        r = d['GNNT']['REP']
        if r['RESULT']['RETCODE'] == '0':
            log.info('委托单号{}撤单成功'.format(order))
            return True
        else:
            self.error('撤单失败: {}'.format(r['RESULT']['MESSAGE']))

    def orders(self):
        """ 成交查询 """
        d = self.request_tradeweb('tradequery', {'USER_ID': self.uid,
                                                 'LAST_TRADE_ID': 0,
                                                 'SESSION_ID': self.sid,
                                                 'MARKET_ID': ''})
        r = d['GNNT']['REP']
        if r['RESULT']['RETCODE'] == '0':
            recs = r['RESULTLIST']['REC']
            if isinstance(recs, dict):
                recs = [recs]
            return [{
                'order': rec['OR_N'],
                'order_at': rec['TI'],
                'type_': {'1': 'buy', '2': 'sell'}.get(rec['TY']),
                'symbol': rec['CO_I'][len(self.mid):],
                'current_price': float(rec['PR']),
                'quantity': int(rec['QTY']),
                'price': float(rec['O_PR']),
                'profit': float(rec['LIQPL']),
                'commision': float(rec['COMM']),
            } for rec in recs]
        else:
            self.error('成交查询失败: {}'.format(r['RESULT']['MESSAGE']))
            return []
