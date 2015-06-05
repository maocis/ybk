from ybk.parsers.base import BaseParser


class Parser(BaseParser):

    """ 上海邮币卡 Parser

    申购样本页: http://www.shscce.com/html/shscce/zxgg/202498_1.shtml
    """

    def __init__(self, abbr="上海邮币卡"):
        self.abbr = abbr
