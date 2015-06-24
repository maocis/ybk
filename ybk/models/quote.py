import time
from datetime import datetime, timedelta

from .mangaa import (
    Model,
    IntField,
    FloatField,
    StringField,
    BooleanField,
    DateTimeField,
)


class Quote(Model):

    """ 交易行情信息 """

    meta = {
        'idformat': '{exchange}_{symbol}_{quote_type}_{quote_at}',
        'unique': ['exchange', 'symbol', 'quote_type', 'quote_at'],
        'indexes': [
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
    volume = IntField(blank=False)              # 周期成交量
    amount = FloatField(blank=False)            # 周期成交额

    @classmethod
    def latest_price(cls, exchange, symbol):
        """ 获得品种的最新成交价

        从日线数据中取就可以了, 实时交易价格也会保存在日线中
        """
        if not hasattr(cls, 'lp_cache'):
            setattr(cls, 'lp_cache', {})
        pair = (exchange, symbol)
        if not cls.lp_cache or cls.lp_cache.get('time', time.time()) < time.time() - 3600:
            cls.lp_cache = {(q.exchange, q.symbol): q.close
                            for q in cls.find({
                                'quote_type': '1d',
                                'quote_at': {'$gte': ndays_ago(10)}},
                sort=[('quote_at', 1)])}
            cls.lp_cache['time'] = time.time()
        return cls.lp_cache.get(pair)

    @classmethod
    def increase(cls, exchange, symbol):
        """ 获得品种的今日涨幅 """
        if not hasattr(cls, 'i_cache'):
            setattr(cls, 'i_cache', {})
        pair = (exchange, symbol)
        now = datetime.utcnow() + timedelta(hours=8)
        if now.hour < 9 and now.minute < 30:
            now -= timedelta(days=1)
        date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        if not cls.i_cache or cls.i_cache.get('time', time.time()) < time.time() - 3600:
            cls.i_cache = {(q.exchange, q.symbol): q.close / q.lclose - 1
                           for q in cls.find({
                               'quote_type': '1d',
                               'quote_at': date,
                           }) if q.lclose}
            cls.i_cache['time'] = time.time()
        return cls.i_cache.get(pair)


def ndays_ago(n):
    return datetime.utcnow() - timedelta(days=n)
