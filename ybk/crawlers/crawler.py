#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pathlib

import yaml

# from ybk.crawlers.parser import PARSERS

SITES = [
    'zgqbyp',
]


def crawl(site):
    cpath = pathlib.Path(__file__).parent / (site + '.yaml')
    conf = yaml.load(cpath.open())
    print(conf)

    # parse_offer, parse_result = PARSERS[site]


if __name__ == '__main__':
    crawl('zgqbyp')
