from datetime import datetime, timedelta
from collections import defaultdict

from flask import render_template, request
from flask.ext.login import login_required

from ybk.models import Collection
from ybk.settings import get_conf

from .views import frontend


@frontend.route('/calendar/')
@login_required
def calendar():
    nav = 'calendar'

    starts_at = request.args.get('starts_at')
    ends_at = request.args.get('ends_at')
    if starts_at:
        starts_at = datetime.strptime(starts_at, '%Y%m%d')

    today = datetime.utcnow() + timedelta(hours=8)
    today = today.replace(hour=0, minute=0, second=0, microsecond=0)
    if not starts_at:
        starts_at = today - timedelta(days=3)
    ends_at = starts_at + timedelta(days=10)

    # 表头
    heads = []
    d = starts_at
    while d <= ends_at:
        heads.append(('周' + '一二三四五六日'[d.weekday()],
                      '{}/{}'.format(d.month, d.day)))
        d += timedelta(days=1)

    # 表身
    exs = []  # 交易所所在行
    rowdict = defaultdict(list)  # 交易所 -> 每天有/没有
    seen = set()
    ddict = {}
    for c in Collection.find({'offers_at': {'$gte': starts_at,
                                            '$lte': ends_at}},
                             sort=[('offers_at', 1)]):
        if (c.exchange, c.offers_at) in seen:
            continue
        seen.add((c.exchange, c.offers_at))
        if c.exchange not in exs:
            exs.append(c.exchange)
        d = ddict.get(c.exchange, starts_at)
        while d < c.cashout_at:
            if d >= c.offers_at and d < c.cashout_at:
                cs = list(Collection.find({'offers_at': c.offers_at,
                                           'exchange': c.exchange}))
                ndays = (c.cashout_at - c.offers_at).days
                if c.offers_at + timedelta(days=ndays) > ends_at:
                    ndays = (ends_at - c.offers_at).days + 1
                rowdict[c.exchange].append({'colspan': ndays,
                                            'exchange': c.exchange,
                                            'count': len(cs),
                                            'cs': cs,
                                            'symbols':
                                            ','.join([c.symbol for c in cs])})
                ddict[c.exchange] = c.cashout_at
                break
            else:
                rowdict[c.exchange].append({'colspan': 1})
                d += timedelta(days=1)

    banks = {}
    details = {}
    for ex in ddict:
        d = ddict[ex]
        while d <= ends_at:
            spans = sum(x['colspan'] for x in rowdict[ex])
            if spans < 11:
                rowdict[ex].append({'colspan': 1})
            d += timedelta(days=1)

        c = get_conf(ex)
        banks[ex] = c['opening']['bank']
        details[ex] = {}
        for cell in rowdict[ex]:
            if 'cs' in cell:
                for c in cell['cs']:
                    details[ex][c.symbol] = {
                        'name': c.name,
                        'price': c.offer_price,
                        'offer_cash': c.offer_cash or 0,
                        'expected_ratio': c.expected_result_cash_ratio or 0,
                        'expected_revenue': c.expected_annual_profit or 0,
                    }

    if not exs:
        exs = ['无申购']

    prev_starts_at = (starts_at - timedelta(days=10)).strftime('%Y%m%d')
    next_starts_at = (starts_at + timedelta(days=10)).strftime('%Y%m%d')

    thisdate = (datetime.utcnow() + timedelta(hours=8))
    thisdate = '{}/{}'.format(thisdate.month, thisdate.day)

    return render_template('frontend/calendar.html', **locals())
