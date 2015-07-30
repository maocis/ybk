from flask import render_template, request, jsonify
from flask.ext.login import current_user

from .views import frontend

from ybk.log import serve_log as log
from ybk.models import Quote, Collection, Position


@frontend.route('/trade/')
def trade():
    nav = 'trade'
    exchange = request.args.get('exchange')
    symbol = request.args.get('symbol')
    if exchange and symbol:
        history_only = True
    else:
        history_only = False
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

    # chart1
    qs = list(Quote.cached(3600).find({'exchange': exchange,
                                       'symbol': symbol,
                                       'quote_type': period}))

    name = '{}({}_{})'.format(Collection.get_name(exchange, symbol),
                              exchange, symbol)
    xdata = [q.quote_at.strftime('%Y/%m/%d') for q in qs]
    sdata = [
        (q.open_, q.close, q.low, q.high,)
        for q in qs]
    adata = [int(q.amount / 10000) for q in qs]
    num_prefix = 100 - len(xdata)
    if num_prefix > 0:
        xdata = xdata + [''] * num_prefix
        sdata = sdata + [()] * num_prefix
        adata = adata + [0] * num_prefix
    option1 = {
        'title': {
            'text': name
        },
        'xAxis': [{
            'type': 'category',
            'boundaryGap': True,
            'axisTick': {'onGap': False},
            'splitLine': {'show': False},
            'data': xdata,
        }],
        'legend': {
            'data': [name, '成交额(万)']
        },
        'dataZoom': {
            'show': False,
            'realtime': True,
            'start': (len(adata) - 100) * 100 // len(adata),
            'end': 100
        },
        'series': [
            {'name': '{}({}_{})'.format(c.name, c.exchange, c.symbol),
             'type': 'k',
             'data': sdata,
             },
            {'name': '成交额(万)',
             'type': 'bar',
             'symbol': 'none',
             'data': [],
             },
        ],
    }

    # chart2
    option2 = {
        'title': {
            'text': '',
        },
        'toolbox': {
            'y': -30,
            'show': True,
            'feature': {
                'mark': {'show': True},
                'dataZoom': {'show': True},
                'dataView': {'show': True, 'readOnly': False},
                'magicType': {'show': True, 'type': ['line', 'bar']},
                'restore': {'show': True},
                'saveAsImage': {'show': True}
            }
        },
        'tooltip': {
            'trigger': 'axis',
            'showDelay': 0,
        },
        'legend': {
            'y': -30,
            'data': ['成交额(万)'],
        },
        'xAxis': [
            {
                'type': 'category',
                'position': 'top',
                'boundaryGap': True,
                'axisLabel': {'show': False},
                'axisTick': {'onGap': False},
                'splitLine': {'show': False},
                'data': xdata,
            }
        ],
        'yAxis': {
            'splitNumber': 3,
        },
        'series': [
            {
                'name': '成交额(万)',
                'type': 'bar',
                'symbol': 'none',
                'data': adata,
            }
        ],
        'grid': {
            'x': 80,
            'y': 5,
            'x2': 20,
            'y2': 40
        },
        'dataZoom': {
            'show': True,
            'realtime': True,
            'start': (len(adata) - 100) * 100 // len(adata),
            'end': 100
        },
    }
    return jsonify(status=200,
                   option1=option1,
                   option2=option2)


def trade_quote_realtime():
    """ 实时数据/列表 """
    # 全部 -> all
    # 指数 -> index
    # 持仓 -> position
    # 自选 -> diy
    category = request.args.get('category', '').strip()
    search = request.args.get('search', '').strip()
    sort = request.args.get('sort', '').strip()
    order = request.args.get('order', 'asc').strip()

    today = Quote.cached(3600).find_one({'quote_type': '1d'},
                                        sort=[('quote_at', -1)]).quote_at
    cond = {'quote_type': '1d',
            'quote_at': today}
    colls = set()
    symbols = []
    if search:
        pairs = Collection.search(search)
        symbols = [p[1] for p in pairs]
        colls = set(pairs)
        cond['symbol'] = {'$in': symbols}
    elif category == 'all':
        pass
    elif category == 'index':
        cs = list(Collection.cached(3600).find({'name': {'$regex': '指数$'}}))
        colls = set((c.exchange, c.symbol) for c in cs)
        symbols = [c.symbol for c in cs]
        cond['symbol'] = {'$in': symbols}
    elif category == 'position':
        position = Position.user_position(current_user._id)
        colls = set((p['exchange'], p['symbol']) for p in position)
        symbols = [p['symbol'] for p in position]
        cond['symbol'] = {'$in': symbols}
    elif category == 'diy':
        raise NotImplementedError

    qs = [q for q in Quote.find(cond)
          if (not colls) or
          ((q.exchange, q.symbol) in colls)]

    qs = [{
        'open_': q.open_,
        'high': q.high,
        'low': q.low,
        'close': q.close,
        'lclose': q.lclose,
        'volume': q.volume,
        'amount': q.amount,
        'increase': 0 if not q.lclose else q.close / q.lclose - 1,
        'exchange': q.exchange,
        'symbol': q.symbol,
        'name': Collection.get_name(q.exchange, q.symbol),
    } for q in qs]

    # sort
    if sort:
        qs = sorted(qs,
                    key=lambda x: x[sort],
                    reverse=order == 'desc')

    # format
    for q in qs:
        if q['lclose']:
            q['lclose'] = '{:.2f}'.format(q['lclose'])
        q['open_'] = '{:.2f}'.format(q['open_'])
        q['high'] = '{:.2f}'.format(q['high'])
        q['low'] = '{:.2f}'.format(q['low'])
        q['close'] = '{:.2f}'.format(q['close'])
        q['amount'] = '{:.1f}万'.format(q['amount'] / 10000)
        q['increase'] = '{:.1f}%'.format(q['increase'] * 100)

    # add no result symbols
    exist_pairs = set((q['exchange'], q['symbol']) for q in qs)
    for exchange, symbol in (colls - exist_pairs):
        qs.append({
            'open_': '-',
            'high': '-',
            'low': '-',
            'close': '-',
            'lclose': '-',
            'volume': '-',
            'amount': '-',
            'increase': '-',
            'exchange': exchange,
            'symbol': symbol,
            'name': Collection.get_name(exchange, symbol),
        })

    return jsonify(status=200,
                   total=len(qs),
                   rows=qs)


def trade_quote_daytrade():
    """ 分时数据 """
    raise NotImplementedError
