#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import random
import logging

from concurrent.futures import ThreadPoolExecutor

import requests
from requests.packages.urllib3.util import is_connection_dropped

import xmltodict

from .protocol import (UserProtocol, TradeProtocol,
                       MoneyProtocol, OfferProtocol)

requests.packages.urllib3.disable_warnings()

log = logging.getLogger('sysframe')


class Client(UserProtocol, TradeProtocol, MoneyProtocol, OfferProtocol):

    def __init__(self,
                 front_url,
                 tradeweb_url):
        """
        :param front_url: http://HOST:PORT
        :param tradeweb_url: [http://HOST:PORT/issue_tradeweb/httpXmlServlet]
        """
        self.front_url = front_url or ''
        self.tradeweb_urls = tradeweb_url
        self.tradeweb_url = random.choice(tradeweb_url)
        for url in tradeweb_url:
            if url.startswith(self.front_url):
                self.front_url = self.tradeweb_url.rsplit('/', 2)[0]
                break
        self.session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(pool_connections=10,
                                                pool_maxsize=10)
        self.session.mount('http://', adapter)
        self.session.headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        self.executor = ThreadPoolExecutor(2)
        self.executor.submit(self.warmup, 1)
        self._reset()

    def _reset(self):
        self.cid = None  # customer_id
        self.uid = None  # user_id
        self.sid = None  # session_id
        self.mid = '99'  # market_id
        self.jsid = None # cookie
        self.username = None
        self.password = None
        self.latency = None
        self.time_offset = None
        self.last_error = ''

    def error(self, msg):
        self.last_error = msg
        log.error(msg)

    @property
    def is_logged_in(self):
        return self.sid is not None

    def request_tradeweb(self, protocol, params):
        return self.request_xml(protocol, params, mode='tradeweb')

    def request_front(self, protocol, params):
        return self.request_xml(protocol, params, mode='front')

    def request_xml(self, protocol, params, mode='tradeweb', headers={},
                    to=1):
        """ 发送交易指令

        - 拼接请求成xml
        - 发送
        - 解析返回的请求
        """
        if mode == 'tradeweb':
            url = self.tradeweb_url
        elif mode == 'front':
            url = self.front_url + \
                '/common_front/checkneedless/user/logon/logon.action'

        xml = self._create_xml(protocol, params)
        log.debug('发送请求 {}: {}'.format(url, xml))
        try:
            r = self.session.post(
                url, headers=headers, data=xml, verify=False,
                timeout=(to, to))
        except requests.exceptions.RequestException:
            self.tradeweb_url = random.choice(self.tradeweb_urls)
            if to <= 32:
                to *= 2
            else:
                raise ValueError('连接超时')
            return self.request_xml(protocol, params, mode, headers, to=to)
        result = r.content.decode('gb18030', 'ignore')
        log.debug('收到返回 {}'.format(result))
        if len(result) > 0:
            return xmltodict.parse(result)
        else:
            raise ValueError('请求出错, 请检查请求格式/网络连接')

    def warmup(self, size=5):
        """ Warmup Connection Pools """
        t0 = time.time()
        url = self.tradeweb_url
        a = self.session.get_adapter(url)
        p = a.get_connection(url)
        count = 0
        conns = [p._get_conn() for _ in range(size)]
        for c in conns:
            if is_connection_dropped(c):
                count += 1
                c.connect()
            p._put_conn(c)
        p.pool.queue = list(reversed(p.pool.queue))
        if count > 0:
            log.info('重新连接{}个连接, 花费{}秒'
                     ''.format(count, time.time() - t0))

    def clear_connections(self):
        url = self.tradeweb_url
        a = self.session.get_adapter(url)
        p = a.get_connection(url)
        p.pool.queue = []

    def request_ff(self, requests, interval=0.001, repeat=1, response=False):
        """ Fire and Forget Requests in Batch

        :param requests: [(protocol, params), ...]
        """
        if len(requests) * repeat > 90:
            repeat = 90 // len(requests)
            log.warning('批量请求次数太多, 自动降频到重复{}次'.format(repeat))
            if repeat < 1:
                raise ValueError('单次批量请求太多, 请设置在90以下')
        xmls = [self._create_xml(protocol, params)
                for protocol, params in requests]
        bxmls = [xml.encode('utf-8') for xml in xmls]

        url = self.tradeweb_url

        a = self.session.get_adapter(url)
        p = a.get_connection(url)
        c = p._get_conn()
        if is_connection_dropped(c):
            c.connect()

        hu = url[url.find('//') + 2:]
        host, uri = hu.split('/', 1)

        def build_request(bxml):
            data = 'POST /{} HTTP/1.1\r\n'.format(uri) + \
                'HOST: {}\r\n'.format(host) + \
                'COOKIE: JSESSIONID={}\r\n'.format(self.jsid) + \
                'Connection: Keep-Alive\r\n' + \
                'Content-Length: {}\r\n'.format(len(bxml)) + \
                '\r\n'
            data = data.encode('gb18030') + bxml
            return data

        begin = time.time()
        sleep_overhead = 0.0002
        for _ in range(repeat):
            for bxml in bxmls:
                t0 = time.time()
                data = build_request(bxml)
                c.sock.sendall(data)
                used = time.time() - t0
                if used < interval - sleep_overhead:
                    time.sleep(interval - used - sleep_overhead)
        end = time.time()
        log.info('批量请求发送完毕, {}秒内发送了{}个请求'
                 ''.format(end - begin, len(bxmls) * repeat))

        # Parsing Results
        if response:
            results = []
            count = len(xmls) * repeat
            f = c.sock.makefile('rb')
            while count > 0:
                count -= 1
                length = 0
                line = f.readline().strip()
                if not line.startswith(b'HTTP/1.1'):
                    break
                while True:
                    line = f.readline().strip()
                    if not line:
                        break
                    key, value = line.split(b': ')
                    if key == b'Content-Length':
                        length = int(value)
                content = f.read(length)
                text = content.decode('gb18030', 'ignore')
                results.append(xmltodict.parse(text))

            p._put_conn(c)
            return results
        else:
            # we are closing one connection, for performance consideration
            # let's open another connection (if necessory) in background
            self.executor.submit(self.warmup, 3)
            c.close()

    def _create_xml(self, protocol, params):
        header = '<?xml version="1.0" encoding="gb2312"?>'
        reqs = []
        for key, value in params.items():
            reqs.append('<{}>{}</{}>'.format(key, value, key))
        req = ''.join(reqs)
        body = '<GNNT><REQ name="{}">{}</REQ></GNNT>'.format(protocol, req)
        return header + body
