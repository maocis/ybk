from flask import render_template, request, jsonify
from flask.ext.login import login_required

from ybk.models import Collection, Quote
from ybk.utils import Pagination

from .views import frontend


@frontend.route('/collection/')
@login_required
def collection():
    nav = 'collection'

    search = request.args.get('search', '')
    exchange = request.args.get('exchange', '')
    page = int(request.args.get('page', 1) or 1)

    limit = 25
    skip = limit * (page - 1)
    cond = {}
    if exchange:
        cond['exchange'] = exchange
    total = Collection.count(cond)
    pagination = Pagination(page, limit, total)

    collections = list(
        Collection.query(cond,
                         sort=[('offers_at', -1)],
                         skip=skip, limit=limit))
    for c in collections:
        lp = Quote.latest_price(c.exchange, c.symbol)
        if lp and c.offer_price:
            c.total_increase = lp / c.offer_price - 1
    return render_template('frontend/collection.html', **locals())


@frontend.route('/collection/list')
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
    total = Collection.count(cond)
    qs = Collection.find(cond)
    if dbsort:
        qs = [Collection(c) for c in
              qs.sort(dbsort).skip(offset).limit(limit)]
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
