from datetime import datetime, timedelta

from .mangaa import (
    Model,
    IntField,
    FloatField,
    StringField,
    DateTimeField,
)


class Quote(Model):

    """ 交易行情信息 """

    meta = {
        'idformat': '{exchange}_{symbol}_{quote_type}_{quote_at}',
        'unique': ['exchange', 'symbol', 'quote_type', 'quote_at'],
        'indexes': [
            [[('exchange', 1), ('quote_at', 1)], {}],
            [[('exchange', 1), ('symbol', 1),
              ('quote_type', 1), ('quote_at', 1)], {}],
        ],
    }

    exchange = StringField(blank=False)         # 交易所ID(简称)
    symbol = StringField(blank=False)           # 交易代码

    quote_type = StringField(blank=False)       # 1m/5m/15m/30m/1h/4h/1d/1w/1m
    quote_at = DateTimeField(blank=False)       # 交易时间

    lclose = FloatField(blank=True)             # 上次收盘价
    open_ = FloatField(blank=False)             # 周期开盘价
    high = FloatField(blank=False)              # 周期最高价
    low = FloatField(blank=False)               # 周期最低价
    close = FloatField(blank=False)             # 周期收盘价
    mean = FloatField(blank=True)               # 周期均价
    volume = IntField(blank=False)              # 周期成交量
    amount = FloatField(blank=False)            # 周期成交额

    @classmethod
    def latest_price(cls, exchange, symbol):
        """ 获得品种的最新成交价

        从日线数据中取就可以了, 实时交易价格也会保存在日线中
        """
        today = datetime.utcnow() + timedelta(hours=8)
        today = today.replace(hour=0, minute=0, second=0, microsecond=0)
        qs = cls.cached(300).find({'exchange': exchange,
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
        qs = cls.cached(300).find({
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
