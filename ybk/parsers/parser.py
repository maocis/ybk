#!/usr/bin/env python
# -*- coding: utf-8 -*-
import importlib

from ybk.settings import SITES, ABBRS
from ybk.log import parse_log as log
from ybk.models import Announcement, Collection


def parse_all():
    for site in SITES:
        try:
            parse(site)
        except:
            log.exception('')


def parse(site):
    rabbrs = {v: k for k, v in ABBRS.items()}
    abbr = rabbrs[site]
    parser = importlib.__import__('ybk.parsers.{}'.format(site),
                                  fromlist=['Parser']).Parser()
    log.info('解析交易所 {}'.format(abbr))
    num_parsed = 0
    num_failed = 0
    for a in Announcement.query({'exchange': abbr,
                                 'parsed': {'$ne': True}}):
        log.info('parsing {}'.format(a.url))
        try:
            for c in parser.parse(a.type_, a.html):
                c['from_url'] = a.url
                Collection(c).upsert()
            a.update({'$set': {'parsed': True}})
            num_parsed += 1
        except Exception as e:
            num_failed += 1
            if not isinstance(e, NotImplementedError):
                log.exception('解析错误')
            continue

    log.info('解析完毕, {}个成功, {}个失败'.format(num_parsed, num_failed))
