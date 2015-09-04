from datetime import datetime, timedelta

from bson import ObjectId

from flask import render_template, request, jsonify
from flask.ext.login import login_required, current_user

from ybk.settings import ABBRS
from ybk.models import Position, Transaction, ProfitLog
from ybk.log import serve_log as log
from .views import user


@user.route('/user/position/')
@login_required
def position():
    nav = 'position'
    today = (datetime.utcnow() + timedelta(hours=8)).strftime('%Y-%m-%d')
    user = current_user._id
    num_collections = Position.num_collections(user)
    average_increase = Position.average_increase(user)
    market_value = Position.market_value(user)
    realized_profit = Position.realized_profit(user)
    unrealized_profit = Position.unrealized_profit(user)
    annual_profit = Position.annual_profit(user)
    position = Position.user_position(user)

    # charts
    pfs = ProfitLog.profits(user)
    pldates = [pf['date'].strftime('%Y-%m-%d') for pf in pfs]
    plvalues = [int(pf['profit']) for pf in pfs]

    exchanges = [{'value': n, 'text': n}
                 for n in sorted(ABBRS)]
    total_transactions = Transaction.user_total_transactions(user)
    transactions = Transaction.user_recent_transactions(
        user)
    for t in transactions:
        t.typecn = '买入' if t.type_ == 'buy' else '卖出'
    return render_template('user/position.html', **locals())


@user.route('/user/position/list/', methods=['GET'])
@login_required
def position_list():
    search = request.args.get('search', '')
    sort = request.args.get('sort', 'total_increase')
    order = request.args.get('order', 'desc')

    user = current_user._id
    position = Position.user_position(user)
    if search:
        position = list(filter(
            lambda x: search in x['exchange'] or
            search in x['name'] or
            search in x['symbol'],
            position))
    position = sorted(position,
                      key=lambda x: x[sort] or 0,
                      reverse=order == 'desc')
    for p in position:
        p['name'] = (p['name'] or '')[:5]
        p['increase'] = '{:.1f}%'.format((p['increase'] or 0) * 100)
        p['total_increase'] = '{:.1f}%'.format((p['total_increase'] or 0)
                                               * 100)
        p['unrealized_profit'] = '{:.1f}'.format(p['unrealized_profit'] or 0)
        p['avg_buy_price'] = '{:.2f}'.format(p['avg_buy_price'])
        if p['latest_price']:
            p['latest_price'] = '{:.2f}'.format(p['latest_price'])
    position = [p for p in position if p['quantity'] > 0]
    return jsonify(total=len(position), rows=position)


@user.route('/user/position/buy', methods=['POST'])
@login_required
def position_buy():
    return position_op(type_='buy')


@user.route('/user/position/sell', methods=['POST'])
@login_required
def position_sell():
    return position_op(type_='sell')


@user.route('/user/transaction/list/', methods=['POST'])
@login_required
def transaction_list():
    offset = int(request.form.get('offset', 0))
    limit = int(request.form.get('limit', 10))
    total_transactions = Transaction.user_total_transactions(user)
    transactions = Transaction.user_recent_transactions(user, offset, limit)
    return jsonify(status=200,
                   total_transactions=total_transactions,
                   transactions=transactions)


@user.route('/user/transaction/delete/', methods=['POST'])
@login_required
def transaction_delete():
    id_ = request.form.get('id')
    t = Transaction.query_one({'_id': ObjectId(id_)})

    # 做一次反向操作
    if t.type_ == 'sell':
        t.type_ = 'buy'
    elif t.type_ == 'buy':
        t.type_ = 'sell'
    Position.do_op(t, reverse=True)

    t.remove()
    return jsonify(status=200)


def position_op(type_):
    try:
        user = current_user._id
        operated_at = datetime.strptime(request.form.get('operated_at'),
                                        '%Y%m%d')
        exchange = request.form.get('exchange')
        symbol = request.form.get('symbol')
        price = float(request.form.get('price'))
        quantity = int(request.form.get('quantity'))
        t = Transaction({
            'user': user,
            'type_': type_,
            'operated_at': operated_at,
            'exchange': exchange,
            'symbol': symbol,
            'price': price,
            'quantity': quantity,
        })
        t.save()
        if not Position.do_op(t):
            t.remove()
        return jsonify(status=200)
    except Exception as e:
        log.exception('')
        return jsonify(status=500, reason=str(e))
