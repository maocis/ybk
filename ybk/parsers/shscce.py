import re

import requests

from ybk.parsers.base import BaseParser
from ybk.parsers.image import parse_image
from ybk.parsers.table import parse_table


class Parser(BaseParser):

    """ 上海邮币卡 Parser

    申购样本页: http://www.shscce.com/html/shscce/zxgg/202498_1.shtml
    """
    site = "shscce"
    abbr = "上海邮币卡"

    pat_offer_fee = re.compile(r'(\d+\.\d+)%申购服务费')
    pat_offer_ratio_cash = re.compile(r'(\d+)%按申购资金摇号分配')
    pat_offer_info_img = re.compile(r'<img src="(http://[^"]+.png)"')

    def parse_offer(self, html):
        result = {}
        offer_fee = float(
            self.pat_offer_fee.search(html).group(1)) / 100
        offer_ratio_cash = float(
            self.pat_offer_ratio_cash.search(html).group(1)) / 100

        image_url = self.pat_offer_info_img.search(html).group(1)
        image = requests.get(image_url).content
        result = []
        for info in parse_table(parse_image(image)):
            stamp = {
                'offer_fee': offer_fee,
                'offer_ratio_cash': offer_ratio_cash,
            }
            stamp.update(info)
            result.append(stamp)
        return result


def test_parse_offer():
    url = 'http://www.shscce.com/html/shscce/zxgg/202498_1.shtml'
    html = requests.get(url).content.decode('utf-8')
    parser = Parser()
    parser.parse_offer(html)


if __name__ == '__main__':
    test_parse_offer()
