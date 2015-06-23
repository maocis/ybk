from flask import render_template
from flask.ext.login import login_required, current_user

from ybk.settings import ABBRS
from ybk.models import Position, Transaction
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
    return render_template('user/position.html', **locals())
