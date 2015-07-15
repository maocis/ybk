from datetime import datetime, timedelta
from collections import defaultdict

from flask import render_template, request, redirect, jsonify
from werkzeug.contrib.atom import AtomFeed

from ybk.models import Exchange, Announcement, Collection, Quote
from ybk.utils import Pagination
from ybk.settings import get_conf

from .views import frontend


def type_to_cn(type_):
    return {
        'offer': '申购',
        'result': '中签',
        'stock': '托管',
    }.get(type_, '托管')


@frontend.route('/announcement/')
def announcement():
    return redirect('/announcement/raw/')


@frontend.route('/announcement/raw/')
def announcement_raw():
    locals()['type_to_cn'] = type_to_cn
    nav = 'announcement'
    tab = 'raw'
    type_ = request.args.get('type', '')
    typecn = type_to_cn(type_)
    exchange = request.args.get('exchange', '')
    page = int(request.args.get('page', 1) or 1)

    limit = 10
    skip = limit * (page - 1)

    cond = {}
    if type_:
        cond['type_'] = type_
    if exchange:
        cond['exchange'] = exchange

    total = Announcement.find(cond).count()
    pagination = Pagination(page, limit, total)
    exchanges = list(sorted(list(e.abbr for e in Exchange.find())))
    types = ['offer', 'result', 'stock']
    announcements = list(
        Announcement.find(cond)
        .sort([('published_at', -1)])
        .skip(skip).limit(limit))
    for a in announcements:
        a.typecn = type_to_cn(a.type_)

    try:
        updated_at = list(Exchange.find()
                          .sort([('updated_at', -1)])
                          .limit(1))[0].updated_at
    except:
        # 只有当数据库为空时才会这样
        updated_at = None

    return render_template('frontend/announcement.html', **locals())


@frontend.route('/announcement/collection/')
def announcement_collection():
    nav = 'announcement'
    tab = 'collection'

    exchange = request.args.get('exchange', '')
    page = int(request.args.get('page', 1) or 1)

    limit = 25
    skip = limit * (page - 1)
    cond = {}
    if exchange:
        cond['exchange'] = exchange
    total = Collection.find(cond).count()
    pagination = Pagination(page, limit, total)

    collections = list(
        Collection.find(cond)
        .sort([('offers_at', -1)])
        .skip(skip).limit(limit))
    for c in collections:
        lp = Quote.latest_price(c.exchange, c.symbol)
        if lp and c.offer_price:
            c.total_increase = lp / c.offer_price - 1
    return render_template('frontend/announcement.html', **locals())


@frontend.route('/announcement/collection/list')
def collection_list():
    exchange = request.args.get('exchange', '')
    search = request.args.get('search', '')
    sort = request.args.get('sort', 'offers_at')
    order = request.args.get('order', 'desc')

    limit = int(request.args.get('limit', 25))
    offset = int(request.args.get('offset', 0))
    if sort in ['offers_at', 'exchange', 'name', 'symbol',
                'offer_price', 'offer_quantity']:
        dbsort = [(sort, 1 if order == 'asc' else -1)]
    else:
        dbsort = None

    cond = {}
    if exchange:
        cond['exchange'] = exchange
    if search:
        cond['$or'] = [
            {'exchange': {'$regex': search}},
            {'name': {'$regex': search}},
            {'symbol': {'$regex': search}},
        ]
    total = Collection.find(cond).count()
    qs = Collection.find(cond)
    if dbsort:
        qs = qs.sort(dbsort).skip(offset).limit(limit)
    rows = [{
            'offers_at': c.offers_at,
            'exchange': c.exchange,
            'name': c.name,
            'symbol': c.symbol,
            'offer_price': c.offer_price,
            'offer_quantity': c.offer_quantity,
            'offer_cash_ratio': c.offer_cash_ratio,
            'offer_cash': c.offer_cash,
            'result_ratio_cash': c.result_ratio_cash,
            }
            for c in qs]

    for d in rows:
        d['total_increase'] = None
        lp = Quote.latest_price(d['exchange'], d['symbol'])
        if lp and d['offer_price']:
            d['total_increase'] = lp / d['offer_price'] - 1

    if not dbsort:
        rows = sorted(rows,
                      key=lambda x: x.get(sort) or 0,
                      reverse=order == 'desc')
        rows = rows[offset:offset + limit]

    for d in rows:
        d['offers_at'] = d['offers_at'].strftime(
            '%Y-%m-%d') if d['offers_at'] else None

        if d['offer_price']:
            d['offer_price'] = '{:.2f}'.format(d['offer_price'])

        if d['offer_cash_ratio']:
            d['offer_cash_ratio'] = '{:.0f}%'.format(
                d['offer_cash_ratio'] * 100)

        if d['offer_cash']:
            d['offer_cash'] = '{:.1f}'.format(d['offer_cash'])

        if d['result_ratio_cash']:
            d['result_ratio_cash'] = '{:.3f}%'.format(
                d['result_ratio_cash'] * 100)

        if d['total_increase']:
            d['total_increase'] = '{:.1f}%'.format(
                100 * (d['total_increase']))

    return jsonify(total=total, rows=rows)


@frontend.route('/announcement/calendar/')
def announcement_calendar():
    nav = 'announcement'
    tab = 'calendar'

    starts_at = request.args.get('starts_at')
    ends_at = request.args.get('ends_at')
    if starts_at:
        starts_at = datetime.strptime(starts_at, '%Y%m%d')

    today = datetime.utcnow() + timedelta(hours=8)
    today = today.replace(hour=0, minute=0, microsecond=0)
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
                        'offer_cash': c.offer_cash or 0,
                        'expected_ratio': c.expected_result_cash_ratio or 0,
                        'expected_revenue': c.expected_annual_profit or 0,
                    }

    if not exs:
        exs = ['无申购']

    prev_starts_at = (starts_at - timedelta(days=10)).strftime('%Y%m%d')
    next_starts_at = (starts_at + timedelta(days=10)).strftime('%Y%m%d')

    return render_template('frontend/announcement.html', **locals())


@frontend.route('/announcement/feed.atom')
def announcement_feed():
    def bjdate(d):
        from datetime import timedelta
        return (d + timedelta(hours=8)).strftime('%Y年%m月%d日')

    type_ = request.args.get('type', '')
    typecn = type_to_cn(type_)
    exchange = request.args.get('exchange', '')
    cond = {}
    feedtitle = '邮币卡公告聚合'
    if type_:
        cond['type_'] = type_
        feedtitle += ' - {}'.format(typecn)
    if exchange:
        cond['exchange'] = exchange
        feedtitle += ' - {}'.format(exchange)

    feed = AtomFeed(feedtitle,
                    feed_url=request.url,
                    url=request.url_root)

    announcements = list(
        Announcement.find(cond)
        .sort([('published_at', -1)])
        .limit(20))

    for a in announcements:
        feed.add('{} {}'.format(bjdate(a.published_at), a.title.strip()),
                 '更多内容请点击标题连接',
                 content_type='text',
                 author=a.exchange,
                 url=a.url,
                 updated=a.published_at,
                 published=a.published_at)
    return feed.get_response()
