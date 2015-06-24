from datetime import datetime

from bson import ObjectId

from flask import render_template, request, jsonify
from flask.ext.login import login_required, current_user

from ybk.settings import ABBRS
from ybk.models import Position, Transaction
from ybk.log import serve_log as log
from .views import user


@user.route('/user/position/')
@login_required
def position():
    user = current_user._id
    num_exchanges = Position.num_exchanges(user)
    num_collections = Position.num_collections(user)
    num_sold = Position.num_sold(user)
    average_increase = Position.average_increase(user)
    realized_profit = Position.realized_profit(user)
    unrealized_profit = Position.unrealized_profit(user)
    position = Position.user_position(user)

    exchanges = [{'value': n, 'text': n}
                 for n in sorted(ABBRS)]
    total_transactions = Transaction.user_total_transactions(user)
    transactions = Transaction.user_recent_transactions(
        user)
    for t in transactions:
        t.typecn = '买入' if t.type_ == 'buy' else '卖出'
    return render_template('user/position.html', **locals())


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
    t = Transaction.find_one({'_id': ObjectId(id_)})

    # 做一次反向操作
    if t.type_ == 'sell':
        t.type_ = 'buy'
    elif t.type_ == 'buy':
        t.type_ = 'sell'
    Position.do_op(t, reverse=True)

    t.delete()
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
            t.delete()
        return jsonify(status=200)
    except Exception as e:
        log.exception('')
        return jsonify(status=500, reason=str(e))
