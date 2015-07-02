from flask import render_template, request, jsonify
from flask.ext.login import current_user

from .views import frontend

from ybk.log import serve_log as log
from ybk.models import Quote, Collection, Position


@frontend.route('/trade/')
def trade():
    nav = 'trade'
    return render_template('frontend/trade.html', **locals())


@frontend.route('/trade/quote/')
def trade_quote():
    # 可以是
    # K线 -> history
    # 实时 -> realtime
    # 分时 -> daytrade
    type_ = request.args.get('type', '')
    try:
        return globals()['trade_quote_' + type_]()
    except Exception as e:
        log.exception('')
        return jsonify(status=500, reason=str(e))


def trade_quote_history():
    """ K线数据 """
    exchange = request.args.get('exchange', '')
    symbol = request.args.get('symbol', '')
    c = Collection.find_one({'exchange': exchange, 'symbol': symbol})
    period = request.args.get('period', '1d')
    qs = list(Quote.find({'exchange': exchange,
                          'symbol': symbol,
                          'quote_type': period}))
    xAxis = [{
        'type': 'category',
        'boundaryGap': True,
        'axisTick': {'onGap': False},
        'splitLine': {'show': False},
        'data': [q.quote_at.strftime('%Y/%m/%d') for q in qs],
    }]
    series = \
        [{
            'name': '{}({}_{})'.format(c.name, c.exchange, c.symbol),
            'type': 'k',
            'data': [
                (q.open_, q.high, q.low, q.close)
                for q in qs
            ]
        }]
    return jsonify(status=200,
                   series=series,
                   xAxis=xAxis)


def trade_quote_realtime():
    """ 实时数据/列表 """
    # 全部 -> all
    # 指数 -> index
    # 持仓 -> position
    # 自选 -> diy
    category = request.args.get('category')
    today = Quote.find_one({'quote_type': '1d'},
                           sort=[('quote_at', -1)]).quote_at
    if category == 'all':
        qs = list(Quote.find({'quote_type': '1d',
                              'quote_at': today}))
    elif category == 'index':
        cs = list(Collection.find({'name': {'$regex': '指数$'}}))
        colls = set((c.exchange, c.symbol) for c in cs)
        symbols = [c.symbol for c in cs]
        qs = [q for q in Quote.find({'quote_type': '1d',
                                     'quote_at': today,
                                     'symbol': {'$in': symbols}})
              if (q.exchange, q.symbol) in colls]
    elif category == 'position':
        position = Position.user_position(current_user._id)
        colls = set((p['exchange'], p['symbol']) for p in position)
        symbols = [p['symbol'] for p in position]
        qs = [q for q in Quote.find({'quote_type': '1d',
                                     'quote_at': today,
                                     'symbol': {'$in': symbols}})
              if (q.exchange, q.symbol) in colls]
    elif category == 'diy':
        raise NotImplementedError

    return jsonify(status=200,
                   quotes=[{
                       'open_': q.open_,
                       'high': q.high,
                       'low': q.low,
                       'close': q.close,
                       'lclose': q.lclose,
                       'volume': q.volume,
                       'amount': q.amount,
                       'exchange': q.exchange,
                       'symbol': q.symbol,
                       'name': Collection.get_name(q.exchange, q.symbol),
                   } for q in qs])


def trade_quote_daytrade():
    """ 分时数据 """
    raise NotImplementedError
