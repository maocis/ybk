#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import functools
from datetime import datetime, timedelta

from flask import (Flask, render_template, request, jsonify,
                   current_app, redirect)
from flask.ext.login import (LoginManager, login_user,
                             current_user, login_required)

from ybk.lighttrade import Trader
from models import User, Account, Position, Order, Status

##################
# setup app
##################

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ybk998'


login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.refresh_view = 'refresh'


@login_manager.user_loader
def load_user(user_id):
    return User.query_one({'_id': user_id})

login_manager.setup_app(app)


@app.template_filter()
def date(value):
    if not value:
        return ''
    else:
        return value.strftime('%Y-%m-%d')


@app.template_filter()
def money(value):
    if not value:
        return '0元'
    if value > 10000:
        return '{:4.2f}万'.format(value / 10000)
    else:
        return '{:4.2f}元'.format(value)

symbols = ['100001', '100002',
           '100010', '100011', '100014', '100019',
           '100020', '100028', '100030']


def admin_required(func):
    @functools.wraps(func)
    def decorated_view(*args, **kwargs):
        if current_user.is_authenticated() and current_user.is_admin():
            return func(*args, **kwargs)
        else:
            return current_app.login_manager.unauthorized()
    return decorated_view


##################
# summary related
##################


@app.route('/')
@login_required
def summary():
    global symbols
    user = request.args.get('user')
    if user:
        if not current_user.is_admin():
            return 'WTF?'

    if user:
        user = User.query_one({'_id': user})
    else:
        user = current_user

    accounts = list(Account.query({'user_id': user._id}))

    ps = [p for p in
          Position.query({'user_id': user._id},
                         sort=[('date', 1)])]
    os = [o for o in
          Order.query({'user_id': user._id},
                      sort=[('date', 1)])]

    dates = list(reversed([p.date for p in ps]))
    total_profit = 0
    for o in os:
        for oo in o.order_list:
            if oo.symbol in symbols:
                total_profit += oo.profit

    today = request.args.get('today')
    if today:
        today = datetime.strptime(today, '%Y-%m-%d %H:%M:%S')
    else:
        d = datetime.utcnow() + timedelta(hours=8)
        if d.hour < 9:
            d -= timedelta(days=1)
        today = d.replace(hour=0, minute=0, second=0, microsecond=0)

    position_list = Position.query_one({'user_id': user._id,
                                        'date': today}).position_list
    status_list = Status.query_one({'user_id': user._id,
                                    'date': today}).status_list
    order_list = Order.query_one({'user_id': user._id,
                                  'date': today}).order_list

    locals()['symbols'] = symbols

    return render_template('summary.html', **locals())


@app.route('/call_api/', methods=['POST'])
def call_api():
    login_name = request.form.get('login_name')
    method = request.form.get('method')
    login_name = login_name.strip()
    a = Account.query_one({'login_name': login_name})
    t = Trader('中港邮币卡', a.login_name, a.login_password)
    t.keep_alive()
    namedict = {c['symbol']: c['name'] for c in t.list_collection()}
    result = getattr(t, method)()
    for r in result:
        if 'symbol' in r:
            r['name'] = namedict[r['symbol']]
    return jsonify(status=200,
                   **{method: result})


##################
# login related
##################


@app.route('/login/')
def login():
    return render_template('login.html', **locals())


@app.route('/user_login/', methods=['POST'])
def user_login():
    mobile = request.form.get('mobile')
    password = request.form.get('password')
    user = User.query_one({'_id': mobile})
    if user and user.password == password:
        login_user(user)

    return redirect(request.args.get('next', '/'))


##################
# admin related
##################


@app.route('/admin/')
@admin_required
def admin():
    users = list(User.query())
    accounts = {}
    for a in Account.query():
        if a.user_id not in accounts:
            accounts[a.user_id] = []
        accounts[a.user_id].append(a)
    return render_template('admin.html', **locals())


@app.route('/ajax/add_user', methods=['POST'])
def add_user():
    mobile = request.form.get('mobile')
    username = request.form.get('username')
    password = request.form.get('password')
    u = User({'mobile': mobile, 'username': username,
              'password': password})
    u.upsert()
    i = 0
    lnames = []
    while True:
        login_name = request.form.get('accounts[{}][login_name]'.format(i))
        login_password = request.form.get(
            'accounts[{}][login_password]'.format(i))
        if login_name and login_password:
            a = Account({'user_id': u._id,
                         'login_name': login_name,
                         'login_password': login_password})
            a.upsert()
            lnames.append(login_name)
            i += 1
        else:
            break
    Account.delete_many({'user_id': u._id,
                         'login_name': {'$nin': lnames}})
    return jsonify(status=200)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format='[%(asctime)s] %(name)s'
                        '<%(levelname)s> %(message)s')

    app.run(host='0.0.0.0', port=5101, threaded=True, debug=True)
