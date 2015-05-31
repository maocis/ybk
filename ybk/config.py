#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pathlib
import logging

import yaml


def setup_config():
    conf = load_config()
    setup_logging()
    setup_mongodb(conf)
    return conf


def load_config():
    path = pathlib.Path(__file__).parent / 'config.yaml'
    return yaml.load(path.open())


def setup_logging():
    logging.getLogger('requests').setLevel(logging.CRITICAL)
    logging.basicConfig(level=logging.INFO)


def setup_mongodb(conf):
    from ybk.mangaa import setup
    setup(conf['mongodb_url'])
