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
        q = cls.find_one({'exchange': exchange,
                          'symbol': symbol,
                          'quote_type': '1d'},
                         sort=[('quote_at', -1)])
        if q:
            return q.close
