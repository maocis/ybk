#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import logging

log = logging.getLogger('sysframe')


class UserProtocol(object):
    def login(self, username, password):
        params = {
            'USER_ID': username,
            'PASSWORD': password,
            'REGISTER_WORD': ''
        }
        headers = {}
        d = self.request_xml('logon', params, mode='tradeweb', headers=headers)
        r = d['GNNT']['REP']
        assert r['@name'] == 'logon'
        rc = int(r['RESULT']['RETCODE'])
        if rc < 0:
            log.error('登录失败:{}'.format(r['RESULT']['MESSAGE']))
            return False
        else:
            self.sid = rc
            if 'USERID' in r['RESULT']:
                self.uid = r['RESULT']['USERID']
            else:
                self.uid = r['RESULT']['NAME']
            # 这样不知道对不对, 中港是这个规则
            self.cid = r['RESULT']['NAME'] + '00'
            self.username = username
            self.password = password
            log.info('用户{}登陆成功'.format(username))
            self.market_query()
            self.sync_server_time()
            return True

    def use_module(self, module=99, mode='front'):
        if self.check_user(module, mode):
            self.module_in_use = module
        else:
            log.error('无法使用交易模块')

    def check_user(self, module=99, mode='front'):
        d = self.request_xml('check_user', {'USER_ID': self.uid,
                                            'SESSION_ID': self.sid,
                                            'MODULE_ID': module,
                                            'F_LOGONTYPE': '',
                                            'LOGONTYPE': 'pc'},
                             headers={},
                             mode=mode)
        r = d['GNNT']['REP']['RESULT']
        if r['RETCODE'] == '0':
            log.info('用户模块检查通过')
            return True
        else:
            log.error('用户模块检查失败:{}'.format(r['MESSAGE']))
            return False

    def keep_alive(self):
        """ 保持用户登陆状态 """
        # 其他客户端不一定是module=18, 18是中港的值
        if not self.check_user(module=18, mode='tradeweb'):
            self.login(self.username, self.password)

    def market_query(self):
        d = self.request_tradeweb('market_query',
                                  {'USER_ID': self.uid,
                                   'SESSION_ID': self.sid,
                                   'MARKET_ID': ''})
        r = d['GNNT']['REP']
        if r['RESULT']['RETCODE'] == '0':
            log.info('市场查询成功')
            self.mid = r['RESULTLIST']['REC']['MA_I']
            return r['RESULTLIST']['REC']
        else:
            log.error('市场查询失败: {}'.format(r['RESULT']['MESSAGE']))


    def sync_server_time(self):
        t0 = time.time()
        d = self.request_tradeweb('sys_time_query', {'USER_ID': self.uid,
                                                     'LAST_ID': 0,
                                                     'SESSION_ID': self.sid,
                                                     'CU_LG': 0})
        self.latency = (time.time() - t0) / 2
        r = d['GNNT']['REP']['RESULT']
        if r['RETCODE'] == '0':
            self.time_offset = int(r['TV_U']) / 1000. - t0
            log.info('服务器时间差: {}毫秒'.format(self.time_offset*1000))
            log.info('服务器延迟: {}毫秒'.format(self.latency*1000))
        else:
            log.error('同步时间失败: {}'.format(r['MESSAGE']))

