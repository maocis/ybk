from datetime import datetime, timedelta

from flask import render_template, request
from .views import frontend

from ybk.models import Exchange, Collection
from ybk.settings import get_conf


@frontend.route('/analysis/')
def analysis():
    nav = 'analysis'
    exchange = request.args.get('exchange')
    exs = sorted(list(Exchange.find()), key=lambda x: x.abbr)
    exchanges = [e.abbr for e in exs]
    ratings = [ex.rating for ex in exs]
    if not exchange:
        exchange = exchanges[0]
    ex = None
    for ex in exs:
        if ex.abbr == exchange:
            break

    # invest history
    ih_dates = []
    ih_values_self = []
    ih_values_all = []
    for h in ex.invest_cash_history:
        ih_dates.append(h['date'].strftime('%Y-%m-%d'))
        ih_values_self.append(h['invest_cash'] / 1e8)
        ih_values_all.append(h['total_cash'] / 1e8)

    # increase history
    inc_days = []
    inc_series = []
    symbols = []
    for symbol, values in ex.increase_history.items():
        if len(values) > len(inc_days):
            inc_days = list(range(1, len(values)))
        inc_series.append({
            'name': symbol,
            'type': 'line',
            'data': [v * 100 for v in values],
        })
        symbols.append(symbol)

    # predict
    conf = get_conf(ex.abbr)
    today = datetime.utcnow() + timedelta(hours=8)
    today = today.replace(hour=0, minute=0, microsecond=0)
    before = today - timedelta(days=conf['cashout'])
    cashout_at = today + timedelta(days=conf['cashout'])
    colls = list(Collection.find({'exchange': ex.abbr,
                                  'offers_at': {'$gte': before}}))
    locals()['zip'] = zip
    return render_template('frontend/analysis.html', **locals())
