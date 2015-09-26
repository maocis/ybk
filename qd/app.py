#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import functools
# from datetime import datetime, timedelta

from flask import (Flask, render_template, request, jsonify,
                   current_app, redirect)
from flask.ext.login import (LoginManager, login_user,
                             current_user, login_required)

from ybk.lighttrade import Trader
from qd.models import exchanges, User, Account, Exchange
from qd.tasks import add_user, add_account

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
        return '0'
    else:
        return '{:4.1f}'.format(value)


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
    return render_template('layout.html')


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
    num_users = User.count()
    num_accounts = Account.count()
    return render_template('admin/index.html', **locals())


@app.route('/admin/user/')
@admin_required
def admin_user():
    users = list(User.query())
    return render_template('admin/user.html', **locals())


@app.route('/admin/account/')
@admin_required
def admin_account():
    users = list(User.query())
    accounts = list(Account.query())
    locals()['exchanges'] = exchanges
    return render_template('admin/account.html', **locals())


@app.route('/admin/exchange/')
@admin_required
def admin_exchange():
    exchanges = list(Exchange.query())
    return render_template('admin/exchange.html', **locals())


@app.route('/admin/collection/')
@admin_required
def admin_collection():
    return render_template('admin/collection.html', **locals())


####################
# APIs
####################

@app.route('/api/call_trader', methods=['POST'])
@admin_required
def call_trader():
    """ 直接调用trader的方法, 返回{方法名: 调用结果} """
    exchange = request.form.get('exchange')
    login_name = request.form.get('login_name')
    method = request.form.get('method')
    login_name = login_name.strip()
    a = Account.query_one({'exchange': exchange,
                           'login_name': login_name})
    if a:
        t = Trader(exchange, a.login_name, a.login_password)
        if not t.is_logged_in:
            return jsonify(status=403, reason='登录失败 {}:{} {}'
                           ''.format(exchange, login_name, t.last_error))
        namedict = {c['symbol']: c['name'] for c in t.list_collection()}
        result = getattr(t, method)()
        for r in result:
            if 'symbol' in r:
                r['name'] = namedict[r['symbol']]
        return jsonify(status=200,
                       **{method: result})
    else:
        return jsonify(status=404, reason='未找到账号 {}:{}'
                       ''.format(exchange, login_name))


@app.route('/api/upsert_user', methods=['POST'])
def upsert_user():
    mobile = request.form.get('mobile')
    username = request.form.get('username')
    password = request.form.get('password')
    is_admin = request.form.get('is_admin') == 'true'
    if add_user(mobile=mobile, username=username,
                password=password, is_admin=is_admin):
        return jsonify(status=200)
    else:
        return jsonify(status=403, reason='创建/修改用户失败')


@app.route('/api/delete_user', methods=['POST'])
@admin_required
def delete_user():
    user = request.form.get('user')
    User.delete_one({'_id': user})
    return jsonify(status=200)


@app.route('/api/upsert_account', methods=['POST'])
@admin_required
def upsert_account():
    user = request.form.get('user')
    exchange = request.form.get('exchange')
    login_name = request.form.get('login_name')
    login_password = request.form.get('login_password')
    money_password = request.form.get('money_password')
    bank_password = request.form.get('bank_password')
    if add_account(user, exchange, login_name,
                   login_password, money_password, bank_password):
        return jsonify(status=200)
    else:
        return jsonify(status=403, reason='创建/修改账号失败')


@app.route('/api/delete_account', methods=['POST'])
@admin_required
def delete_account():
    user = request.form.get('user')
    exchange = request.form.get('exchange')
    login_name = request.form.get('login_name')
    Account.delete_one({'user': user,
                        'exchange': exchange,
                        'login_name': login_name})
    return jsonify(status=200)


@app.route('/api/import_account', methods=['POST'])
@admin_required
def import_account():
    text = request.form.get('text')
    total = 0
    imported = 0
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        vals = line.split()
        vals += [''] * (6 - len(vals))
        user, exchange, login_name, login_password, \
            money_password, bank_password = vals
        r = add_account(user, exchange, login_name, login_password,
                        money_password, bank_password)
        total += 1
        imported += int(r)
    return jsonify(status=200, total=total, imported=imported)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format='[%(asctime)s] %(name)s'
                        '<%(levelname)s> %(message)s')

    app.run(host='0.0.0.0', port=5858, threaded=True, debug=True)
