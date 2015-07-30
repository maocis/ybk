from datetime import datetime, timedelta

from yamo import (
    Document, IDFormatter, Index,
    IntField,
    FloatField,
    StringField,
    DateTimeField,
)


class Quote(Document):

    """ 交易行情信息 """
    class Meta:
        idf = IDFormatter('{exchange}_{symbol}_{quote_type}_{quote_at}')
        idx1 = Index(['exchange', 'symbol', 'quote_type', 'quote_at'],
                     unique=True)
        idx2 = Index(['exchange', 'quote_at'])

    exchange = StringField(required=True)         # 交易所ID(简称)
    symbol = StringField(required=True)           # 交易代码

    # 1m/5m/15m/30m/1h/4h/1d/1w/1m
    quote_type = StringField(required=True)
    quote_at = DateTimeField(required=True)       # 交易时间

    lclose = FloatField()                         # 上次收盘价
    open_ = FloatField(required=True)             # 周期开盘价
    high = FloatField(required=True)              # 周期最高价
    low = FloatField(required=True)               # 周期最低价
    close = FloatField(required=True)             # 周期收盘价
    mean = FloatField()                           # 周期均价
    volume = IntField(required=True)              # 周期成交量
    amount = FloatField(required=True)            # 周期成交额

    @classmethod
    def latest_price(cls, exchange, symbol):
        """ 获得品种的最新成交价

        从日线数据中取就可以了, 实时交易价格也会保存在日线中
        """
        today = datetime.utcnow() + timedelta(hours=8)
        today = today.replace(hour=0, minute=0, second=0, microsecond=0)
        qs = cls.cached(300).query({'exchange': exchange,
                                    'symbol': symbol,
                                    'quote_type': '1d',
                                    'quote_at': {'$lte': today}},
                                   {'close': 1},
                                   sort=[('quote_at', -1)],
                                   limit=1)
        if qs:
            return qs[0].close

    @classmethod
    def increase(cls, exchange, symbol):
        """ 获得品种的今日涨幅 """
        now = datetime.utcnow() + timedelta(hours=8)
        if now.hour < 9 and now.minute < 30:
            now -= timedelta(days=1)
        date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        qs = cls.cached(300).query({
            'exchange': exchange,
            'symbol': symbol,
            'quote_type': '1d',
            'quote_at': date},
            {'close': 1, 'lclose': 1},
            limit=1)
        if qs and qs[0].lclose:
            q = qs[0]
            return q.close / q.lclose - 1


def ndays_ago(n):
    return datetime.utcnow() - timedelta(days=n)
