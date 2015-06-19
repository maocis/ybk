#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pathlib
import logging

import yaml
from ybk.log import LogFormatter


conf = None


def setup_config(args=None):
    global conf
    if not conf:
        conf = load_config()
        if args:
            for field in ['loglevel', 'port', 'mongodb_url',
                          'secret_key', 'num_processes',
                          'token', 'wechat_appid', 'wechat_appsecret']:
                value = getattr(args, field, None)
                if value:
                    conf[field] = value
        setup_logging(conf)
        setup_mongodb(conf)
    return conf


def load_config():
    paths = [
        pathlib.Path(__file__).parent.parent / 'config.yaml',
        pathlib.Path('.') / 'config.yaml',
        pathlib.Path('~') / 'config.yaml',
    ]
    for path in paths:
        try:
            return yaml.load(path.open())
        except:
            pass

    return {
        'loglevel': 'INFO',
        'port': 5100,
        'secret_key': 'ybk369',
        'num_processes': 2,
        'mongodb_url': 'mongodb://localhost/ybk',
    }


def setup_logging(conf):
    loglevel = getattr(logging,
                       conf.get('loglevel', '').upper(),
                       logging.INFO)
    logging.getLogger('requests').setLevel(logging.CRITICAL)
    log = logging.getLogger()
    log.setLevel(loglevel)
    handler = logging.StreamHandler()
    handler.setFormatter(LogFormatter())
    log.addHandler(handler)


def setup_mongodb(conf):
    from ybk.models import setup
    setup(conf['mongodb_url'])
