import time
import copy
from collections import defaultdict
from datetime import datetime, timedelta


from ybk.log import serve_log as log

from yamo import (
    Document, Index,
    IntField,
    FloatField,
    StringField,
    DateTimeField,
)

from .quote import Quote
from .models import Collection
from .user import User


class Transaction(Document):

    """ 用户交易信息 """
    class Meta:
        idx1 = Index(['user', 'type_', 'exchange', 'symbol'])
        idx2 = Index(['user', 'operated_at'])

    exchange = StringField(required=True)         # 交易所ID(简称)
    symbol = StringField(required=True)           # 交易代码

    user = StringField(required=True)
    type_ = StringField(required=True)            # buy/sell
    price = FloatField(required=True)
    quantity = IntField(required=True)
    operated_at = DateTimeField(created=True)

    @classmethod
    def user_total_transactions(cls, user):
        """ 用户总操作次数 """
        return cls.count({'user': user})

    @classmethod
    def user_recent_transactions(cls, user, offset=0, limit=None):
        """ 用户最近的操作 """
        qs = cls.query({'user': user}, sort=[('operated_at', -1)])
        if offset:
            qs.skip(offset)
        if limit:
            qs.limit(limit)
        return list(qs)


class Position(Document):

    """ 用户持仓信息 """
    class Meta:
        idx1 = Index(['user', 'exchange', 'symbol'], unique=True)

    exchange = StringField(required=True)         # 交易所ID(简称)
    symbol = StringField(required=True)           # 交易代码

    user = StringField(required=True)
    quantity = FloatField(required=True, default=0)

    @classmethod
    def num_exchanges(cls, user):
        """ 用户持有多少个交易所的持仓 """
        return len(set(p.exchange for p in
                       cls.query({'user': user}, {'exchange': 1})))

    @classmethod
    def num_collections(cls, user):
        """ 用户持有多少不同的藏品 """
        return len(list(cls.query({'user': user, 'quantity': {'$gt': 0}},
                                  {'_id': 1})))

    @classmethod
    def num_sold(cls, user):
        """ 用户已卖出过多少个藏品 """
        return len(set('{exchange}_{symbol}'.format(**t) for t in
                       Transaction.find({'user': user, 'type_': 'sell'},
                                        {'exchange': 1, 'symbol': 1})))

    @classmethod
    def user_position(cls, user):
        """ 目前持仓概况, cached """
        cachekey = 'pcache_{}'.format(user)
        if not hasattr(cls, cachekey):
            setattr(cls, cachekey, {})

        now = time.time()
        cache = getattr(cls, cachekey)
        if 'position' not in cache or \
                cache.get('time', now) < now - 5:
            cache['position'] = cls._user_position(user)
            cache['time'] = time.time()
        return copy.deepcopy(cache['position'])

    @classmethod
    def _user_position(cls, user):
        """ 目前持仓概况 """
        collections = {}
        for p in cls.query({'user': user}):
            pair = (p.exchange, p.symbol)
            collections.setdefault(pair, 0)
            collections[pair] += p.quantity
        buy_info = {}
        for t in Transaction.query({'user': user, 'type_': 'buy'},
                                   sort=[('operated_at', 1)]):
            pair = (t.exchange, t.symbol)
            if pair in collections:
                buy_info.setdefault(pair, [0, 0, None])
                buy_info[pair][0] += t.quantity
                buy_info[pair][1] += t.quantity * t.price
                if not buy_info[pair][2]:
                    buy_info[pair][2] = t.operated_at
        sell_info = {}
        for t in Transaction.query({'user': user, 'type_': 'sell'},
                                   sort=[('operated_at', -1)]):
            pair = (t.exchange, t.symbol)
            if pair in collections:
                sell_info.setdefault(pair, [0, 0, None])
                sell_info[pair][0] += t.quantity
                sell_info[pair][1] += t.quantity * t.price
                if not sell_info[pair][2]:
                    sell_info[pair][2] = t.operated_at
        position = []
        for pair, quantity_amount in buy_info.items():
            exchange, symbol = pair
            quantity, amount, first_buy_at = quantity_amount
            if quantity:
                avg_buy_price = amount / quantity
                realized_profit = 0
                last_sell_at = datetime.utcnow()
                if pair in sell_info:
                    quantity2, amount2, last_sell_at = sell_info[pair]
                    quantity -= quantity2
                    realized_profit = amount2 - avg_buy_price * quantity2

                if quantity != collections[pair]:
                    cls.update_one({'exchange': pair[0], 'symbol': pair[1],
                                    'user': user}, {'$set': {'quantity': quantity}})
                latest_price = Quote.latest_price(exchange, symbol)
                increase = Quote.increase(exchange, symbol)
                if not latest_price:
                    latest_price = avg_buy_price
                unrealized_profit = (latest_price - avg_buy_price) * quantity
                past_days = max(1, (last_sell_at - first_buy_at).days)
                annual_profit = (365 / past_days) * \
                    (unrealized_profit + realized_profit)
                position.append({
                    'exchange': exchange,
                    'symbol': symbol,
                    'name': Collection.get_name(exchange, symbol),
                    'avg_buy_price': avg_buy_price,
                    'quantity': quantity,
                    'latest_price': latest_price,
                    'increase': increase,
                    'total_increase': latest_price / avg_buy_price - 1 if avg_buy_price > 0 else 100,
                    'realized_profit': realized_profit,
                    'unrealized_profit': unrealized_profit,
                    'annual_profit': annual_profit,
                })
        return sorted(position, key=lambda x: x['exchange'])

    @classmethod
    def average_increase(cls, user):
        """ 平均涨幅 """
        position = [p for p in cls.user_position(user) if p['quantity'] > 0]
        if len(position):
            return sum(p['total_increase'] for p in position) / len(position)

    @classmethod
    def market_value(cls, user):
        """ 持仓总市值 """
        position = cls.user_position(user)
        return sum(p['latest_price'] * p['quantity'] for p in position)

    @classmethod
    def unrealized_profit(cls, user):
        """ 未实现收益(浮盈) """
        return sum(p['unrealized_profit'] for p in
                   cls.user_position(user))

    @classmethod
    def realized_profit(cls, user):
        """ 已实现收益 """
        return sum(p['realized_profit']
                   for p in cls.user_position(user))

    @classmethod
    def annual_profit(cls, user):
        """ 年化收益 """
        return sum(p['annual_profit'] for p in
                   cls.user_position(user))

    @classmethod
    def do_op(cls, t, reverse=False):
        c = cls.query_one({'user': t.user,
                           'exchange': t.exchange,
                           'symbol': t.symbol})
        if not c:
            if reverse:
                return False
            elif t.type_ == 'buy':
                c = cls({'user': t.user,
                         'exchange': t.exchange,
                         'symbol': t.symbol,
                         'quantity': t.quantity})
            else:
                return False
        elif t.type_ == 'buy':
            c.quantity += t.quantity
        elif t.type_ == 'sell':
            c.quantity -= t.quantity

        if c.quantity >= 0:
            c.upsert()
            return True
        else:
            return False


class ProfitLog(Document):

    """ 用户的收益日志 """
    class Meta:
        idx1 = Index(['user', 'date'], unique=True)

    user = StringField(required=True)
    date = DateTimeField(required=True)
    profit = FloatField()

    @classmethod
    def profits(cls, user):
        """ 获得收益日志 """
        return [{'date': pl.date,
                 'profit': pl.profit}
                for pl in cls.query({'user': user},
                                    sort=[('date', 1)])]

    @classmethod
    def ensure_all_profits(cls):
        for u in User.query():
            cls.ensure_profits(u._id)

    @classmethod
    def ensure_profits(cls, user):
        """ 确保生成收益日志 """
        log.info('为用户{}生成收益日志'.format(user))
        ts = list(reversed(Transaction.user_recent_transactions(user)))
        if ts:
            today = datetime.utcnow() + timedelta(hours=8)
            today = today.replace(hour=0, minute=0, second=0, microsecond=0)
            di = 0
            date = ts[di].operated_at
            positions = {}
            realized_profits = defaultdict(float)
            while date <= today:
                profit = 0
                # include new transactions
                while di < len(ts) and ts[di].operated_at <= date:
                    t = ts[di]
                    op = 1 if t.type_ == 'buy' else -1
                    pair = (t.exchange, t.symbol)
                    if pair not in positions:
                        positions[pair] = (t.price, t.quantity * op)
                    else:
                        pv = positions[pair]
                        amount = pv[0] * pv[1] + t.price * t.quantity * op
                        quantity = pv[1] + t.quantity * op
                        if quantity == 0:
                            realized_profits[pair] += pv[1] * (t.price - pv[0])
                            del positions[pair]
                        else:
                            positions[pair] = (amount / quantity, quantity)
                    di += 1

                # calculate profit
                for pair in positions:
                    q = Quote.query_one({'exchange': pair[0],
                                         'symbol': pair[1],
                                         'quote_type': '1d',
                                         'quote_at': {'$lte': date}},
                                        sort=[('quote_at', -1)])
                    if q:
                        pv = positions[pair]
                        profit += (q.close - pv[0]) * pv[1]

                profit += sum(realized_profits.values())

                # update profit
                cls.update_one({'date': date, 'user': user},
                               {'$set': {'profit': profit}},
                               upsert=True)
                date += timedelta(days=1)
