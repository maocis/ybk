import re
from datetime import timedelta

import requests
import lxml.html
from dateutil.parser import parse as parse_dt

from ybk.parsers.base import BaseParser


class Parser(BaseParser):

    """  Parser

    申购样本页: http://ybk.hxce.cn/html/xxpl/sggg/2015-06-08/493.html
    """
    site = "hxce"
    abbr = "海西文交所"

    offer_fee = 0.001
    pat_offer_cash_ratio = re.compile(r'摇号抽签(\d+)%')
    pat_offers_at = re.compile(r'将于(\d+年\d+月\d+日)')
    pat_ymd = re.compile(r'(年|月|日)')
    pat_tags = re.compile(r'(<[^>]*>|\s+)')

    def parse_offer(self, html):
        try:
            offer_cash_ratio = float(
                self.pat_offer_cash_ratio.search(html).group(1)) / 100
        except:
            offer_cash_ratio = 1.
        offers_at = self.pat_offers_at.search(
            self.pat_tags.sub('', html)).group(1)
        offers_at = self.pat_ymd.sub('/', offers_at)
        offers_at = parse_dt(offers_at)

        t = lxml.html.fromstring(html)
        cells = [x.text_content().strip()
                 for x in t.xpath(
            './/div[@class="detail_cn"]/table/tbody/tr/td')]

        per_row = len(cells) // 2
        d = dict(zip(cells[:per_row], cells[per_row:]))

        if not d:
            # 按图片走
            raise NotImplementedError

        name = d['藏品名称']
        symbol = d['藏品代码']
        offer_price = float(d['申购价格'].replace('元', ''))
        offer_quantity = int(d['申购总数']
                             .replace('万', '0000')
                             .replace('.', ''))
        if symbol.startswith('1'):
            type_ = '邮票'
        elif symbol.startswith('2'):
            type_ = '钱币'
        else:
            raise ValueError

        stamp = {
            'exchange': self.abbr,
            'type_': type_,
            'symbol': symbol,
            'name': name,
            'offer_price': offer_price,
            'offer_quantity': offer_quantity,
            'offer_accmax': offer_quantity,
            'offer_overbuy': True,
            'offer_fee': self.offer_fee,
            'offer_cash_ratio': offer_cash_ratio,
            'offers_at': offers_at,
            'draws_at': offers_at + timedelta(days=1),
            'trades_at': offers_at + timedelta(days=2),
        }
        return [stamp]


def test_parse_offer():
    url = 'http://ybk.hxce.cn/html/xxpl/sggg/2015-06-08/493.html'
    html = requests.get(url).content.decode('gb18030', 'ignore')
    parser = Parser()
    print(parser.parse_offer(html))


if __name__ == '__main__':
    test_parse_offer()
