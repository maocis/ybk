#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse

from ybk.crawlers import crawl, crawl_all, ABBRS
from ybk.config import setup_config


def _get_site_by_abbr(abbr):
    return ABBRS[abbr]


def do_list(parser, args):
    for abbr, site in ABBRS.items():
        print('{abbr}: {site}'.format(**locals()))


def do_crawl(parser, args):
    setup_config(args)
    if args.all:
        crawl_all()
    elif args.sites:
        for site in args.sites:
            crawl(_get_site_by_abbr(site))
    else:
        parser.print_help()


def do_parse(parser, args):
    setup_config(args)
    raise NotImplementedError


def do_serve(parser, args):
    from ybk.app import create_app
    conf = setup_config(args)
    app = create_app(conf)
    if args.debug:
        args.loglevel = 'DEBUG'
    app.config['SECRET_KEY'] = conf['secret_key']
    if args.debug:
        app.run(host='0.0.0.0', port=conf['port'], debug=True)
    elif args.production:
        app.run(host='0.0.0.0',
                port=conf['port'],
                processes=conf['num_processes'])
    else:
        parser.print_help()


def main():
    parser = argparse.ArgumentParser(
        description='邮币卡命令行程序')

    subparsers = parser.add_subparsers(dest='subparser',
                                       help='子命令')
    subparsers.add_parser('list',
                          help='列出目前支持的邮币卡交易所')

    # 抓取相关
    pcrawl = subparsers.add_parser('crawl',
                                   help='从各大邮币卡交易中心爬取最新数据')
    cgroup = pcrawl.add_mutually_exclusive_group(required=False)
    cgroup.add_argument('--sites', nargs='+',
                        help='爬取的站点简称, e.g. "江苏所"')
    cgroup.add_argument('--all', action='store_true', help='爬取全部站点')

    # 解析相关
    pparse = subparsers.add_parser('parse',
                                   help='解析下载(尚未解析)的数据')
    pgroup = pparse.add_mutually_exclusive_group(required=False)
    pgroup.add_argument('--sites', nargs='+',
                        help='解析的站点简称,  e.g. "江苏所", 默认全部解析')
    pgroup.add_argument('--all', action='store_true', help='解析全部站点')

    # flask相关
    pserve = subparsers.add_parser('serve',
                                   help='启动服务器端')
    pserve.add_argument('--secret_key', '-k', type=str,
                        help='flask用secret key')
    pserve.add_argument('--num_processes', '-n', type=int,
                        help='flask启动进程个数')
    pserve.add_argument('--port', '-p', type=int,
                        help='端口')
    pgroup = pserve.add_mutually_exclusive_group(required=False)
    pgroup.add_argument('--debug', action='store_true',
                        help='是否使用debug模式, '
                        '使用debug模式loglevel会被重置为DEBUG')
    pgroup.add_argument('--production', action='store_true',
                        help='是否使用production模式, '
                        '该模式下将禁用reloader, 启用processes')

    # 共用
    for p in [pcrawl, pparse, pserve]:
        p.add_argument('--mongodb_url', '-m', type=str,
                       help='Mongodb数据库地址')
        p.add_argument('--loglevel', '-l', type=str,
                       help='日志level')

    # 子命令路由
    args = parser.parse_args()
    for parser, sp in zip(
            [None, pcrawl, pparse, pserve],
            ['list', 'crawl', 'parse', 'serve']):
        if sp == args.subparser:
            globals()['do_' + args.subparser](parser, args)
            break
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
