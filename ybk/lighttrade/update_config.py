#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" 根据update.yaml中的信息更新trading.yaml的信息 """
import os
import yaml
import requests
import xmltodict

updateyaml = os.path.join(os.path.dirname(__file__), 'update.yaml')
tradingyaml = os.path.join(os.path.dirname(__file__), 'trading.yaml')

config = yaml.load(open(updateyaml))

def update_sysframe():
    issue_trade = '/Trader/Modules/ISSUEModule/Config/ISSUE_TradePlugin.xml'
    issue_hq = '/Trader/Modules/ISSUEModule/Config/ISSUE_HQPlugin.xml'
    mebs_consumer =  '/Trader/Modules/MEBSModule/Config/MEBS_Consumer.xml'
    trading = yaml.load(open(tradingyaml))
    for exchange, url in config['sysframe'].items():
        print('更新{}'.format(exchange))
        if exchange not in trading:
            trading[exchange] = {}

        conf = {'system': 'sysframe'}

        # quotation server
        try:
            d = xmltodict.parse(requests.get(url + issue_hq).text)
        except:
            print('no quotation server, {}'.format(url + issue_hq))
            xml = open('/Users/ob/Documents/gnnt/{}{}'.format(exchange,
                                                              issue_hq))
            d = xmltodict.parse(xml.read())
        si = d['ConfigInfo']['AllTelecomServer']['ServerInfo']
        if isinstance(si, dict):
            si = [si]
        conf['quote_tcp'] = 'tcp://{}:{}'.format(si[0]['IPAddress'],
                                                si[0]['Port'])
        conf['quote_http'] = 'http://{}:{}'.format(si[0]['IPAddress'],
                                                    si[0]['HttpPort'])

        # trade server
        try:
            d = xmltodict.parse(requests.get(url + issue_trade).text)
        except:
            print('no trade server, {}'.format(url + issue_trade))
            xml = open('/Users/ob/Documents/gnnt/{}{}'.format(exchange,
                                                              issue_trade))
            d = xmltodict.parse(xml.read())
        curl = d['ConfigInfo']['CommunicationUrl'].replace('\\', '/')
        si = d['ConfigInfo']['AllTelecomServer']['ServerInfo']
        if isinstance(si, dict):
            si = [si]
        conf['tradeweb_url'] = 'http://{}:{}/'.format(si[0]['IPAddress'],
                                                    si[0]['Port'])+ curl

        # consumer server
        try:
            d = xmltodict.parse(requests.get(url + mebs_consumer).text)
        except:
            print('no consumer server, {}'.format(url + mebs_consumer))
            xml = open('/Users/ob/Documents/gnnt/{}{}'.format(exchange,
                                                              mebs_consumer))
            d = xmltodict.parse(xml.read())
        furl = d['ConfigInfo']['CommunicationUrl']
        iurl = d['ConfigInfo']['LoginedUrl']
        si = d['ConfigInfo']['AllTelecomServer']['ServerInfo']
        if isinstance(si, dict):
            si = [si]
        conf['front_url'] = 'http://{}:{}/'.format(si[0]['IPAddress'],
                                                si[0]['Port'])+ furl
        conf['index_url'] = 'http://{}:{}'.format(si[0]['IPAddress'],
                                                    si[0]['Port'])+ iurl

        trading[exchange].update(conf)

    yaml.dump(trading, open(tradingyaml, 'w'),
              indent=4 ,default_flow_style=False, allow_unicode=True)


def update_winner():
    pass


def update_all():
    update_sysframe()
    update_winner()


if __name__ == '__main__':
    update_all()

