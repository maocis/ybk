#!/usr/bin/env python
# -*- coding: utf-8 -*-

__all__ = ['BaseParser']


class BaseParser(object):

    """ 所有解析器的基类 """

    def __init__(self, site, abbr):
        raise NotImplementedError

    def parse(self, type_, html):
        if type_ == 'offer':
            r = self.parse_offer(html)
        elif type_ == 'result':
            r = self.parse_result(html)
        else:
            raise ValueError('未知的解析类型: {}'.format(type_))

        raise NotImplementedError(str(r))

    def parse_offer(self, html):
        raise NotImplementedError

    def parse_result(self, html):
        raise NotImplementedError
