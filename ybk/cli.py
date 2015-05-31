#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse

from ybk.crawlers import crawl, crawl_all, ABBRS
from ybk.config import setup_config


def _get_site_by_abbr(abbr):
    return ABBRS[abbr]


def do_list():
    for abbr, site in ABBRS.items():
        print('{abbr}: {site}'.format(**locals()))


def do_crawl(parser, args):
    setup_config()
    if args.all:
        crawl_all()
    elif args.sites:
        for site in args.sites:
            crawl(_get_site_by_abbr(site))
    else:
        parser.print_help()


def do_parse(parser, args):
    raise NotImplementedError


def main():
    parser = argparse.ArgumentParser(
        description='邮币卡命令行程序')
    subparsers = parser.add_subparsers(dest='subparser',
                                       help='子命令')
    subparsers.add_parser('list',
                          help='列出目前支持的邮币卡交易所')

    pcrawl = subparsers.add_parser('crawl',
                                   help='从各大邮币卡交易中心爬取最新数据')
    cgroup = pcrawl.add_mutually_exclusive_group(required=False)
    cgroup.add_argument('--sites', nargs='+',
                        help='爬取的站点简称, e.g. "江苏所"')
    cgroup.add_argument('--all', action='store_true', help='爬取全部站点')

    pparse = subparsers.add_parser('parse',
                                   help='解析下载(尚未解析)的数据')
    pgroup = pparse.add_mutually_exclusive_group(required=False)
    pgroup.add_argument('--sites', nargs='+',
                        help='解析的站点简称,  e.g. "江苏所", 默认全部解析')
    pgroup.add_argument('--all', action='store_true', help='解析全部站点')

    args = parser.parse_args()
    if args.subparser == 'list':
        do_list()
    elif args.subparser == 'crawl':
        do_crawl(pcrawl, args)
    elif args.subparser == 'parse':
        do_parse(pparse, args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
