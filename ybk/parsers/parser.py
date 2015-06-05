#!/usr/bin/env python
# -*- coding: utf-8 -*-
import importlib

from ybk.settings import SITES, ABBRS
from ybk.log import parse_log as log
from ybk.models import Announcement


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
    for a in Announcement.find({'exchange': abbr,
                                'parsed': {'$ne': True}}):
        parser.parse(a.type_, a.html)
