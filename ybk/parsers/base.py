#!/usr/bin/env python
# -*- coding: utf-8 -*-

__all__ = ['BaseParser']


class BaseParser(object):

    """ 所有解析器的基类 """

    def parse(self, type_, html):
        """ 解析网页

        :param type_: 解析类别, offer/result
        :param html: 解析网页文本
        :returns: [dict, dict, ...], 其中dict的字段参照ybk.models.Stamp
        """
        if type_ == 'offer':
            r = self.parse_offer(html)
        elif type_ == 'result':
            r = self.parse_result(html)
        else:
            raise ValueError('未知的解析类型: {}'.format(type_))

        # 确保返回格式正确
        assert isinstance(r, list)
        for s in r:
            assert isinstance(s, dict)

        return r

    def parse_offer(self, html):
        raise NotImplementedError

    def parse_result(self, html):
        raise NotImplementedError
