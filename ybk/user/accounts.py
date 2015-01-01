import json
import base64

from flask import render_template, redirect, request, jsonify
from flask.ext.login import login_required, current_user

from ybk.settings import CONFS
from ybk.trade import (update_trade_account, quote_detail,
                       order, withdraw, transfer)
from ybk.models import Investor, TradeAccount, Exchange
from ybk.lighttrade import Trader

from .views import user


@user.route('/user/accounts/')
@login_required
def accounts():
    # nav = 'accounts'
    return redirect('/user/personal_info')
    # return render_template('user/accounts.html', **locals())


@user.route('/user/personal_info/')
@login_required
def personal_info():
    nav = 'accounts'
    tab = 'personal_info'
    user = current_user._id
    investors = Investor.user_investors(user)
    investor_ids = [i._id for i in investors]
    trade_accounts = TradeAccount.user_accounts(user)
    account_table = {}
    for ta in trade_accounts:
        if ta.exchange not in account_table:
            account_table[ta.exchange] = [None] * len(investors)
        order = investor_ids.index(ta.investor)
        account_table[ta.exchange][order] = ta
    colspan = len(investors) + 1
    return render_template('user/personal_info.html', **locals())


@user.route('/user/investor_info/')
@login_required
def investor_info():
    nav = 'accounts'
    tab = 'investor_info'
    user = current_user._id
    investors = Investor.user_investors(user)
    return render_template('user/investor_info.html', **locals())


@user.route('/user/investor/upsert.ajax', methods=['POST'])
@login_required
def investor_upsert():
    def extract_image(src):
        if src:
            return base64.b64decode(src[src.find('base64,') + 7:])
        else:
            return b''
    user = current_user._id
    d = json.loads(request.data.decode('utf-8'))
    bank_accounts = d['bank_accounts']
    for ba in bank_accounts:
        ba['number'] = ba['number'].replace(' ', '')
    i = {
        'user': user,
        'name': d.get('name', ''),
        'mobile': d.get('mobile', ''),
        'id_type': '身份证',
        'id_number': d.get('id_number', ''),
        'id_front': extract_image(d.get('id_front', '')),
        'id_back': extract_image(d.get('id_back', '')),
        'province': d.get('province', ''),
        'city': d.get('city', ''),
        'address': d.get('address', ''),
        'bank_accounts': bank_accounts,
    }
    oldi = Investor.query_one({'user': user}, sort=[('order', -1)])
    thei = Investor.query_one({'id_number': i['id_number']})
    if not thei:
        i['order'] = oldi.order + 1 if oldi else 1
    else:
        i['order'] = thei.order
    try:
        Investor(i).upsert()
    except Exception as e:
        return jsonify(status=500, reason=str(e))
    return jsonify(status=200, reason='')


@user.route('/user/investor/edit.ajax')
@login_required
def investor_edit():
    def pack_image(b):
        if b:
            return base64.b64encode(b).decode('ascii')
        else:
            return ''
    _id = request.args.get('id')
    i = Investor.query_one({'_id': _id})
    if not i:
        return jsonify(status=404, reason='投资人id={}未找到'.format(_id))
    else:
        i = i.to_dict()
        i['id_front_b64'] = pack_image(i['id_front'])
        i['id_back_b64'] = pack_image(i['id_back'])
        del i['id_front']
        del i['id_back']
        return jsonify(status=200, data=i, reason='')


@user.route('/user/investor/delete.ajax', methods=['POST'])
@login_required
def investor_delete():
    _id = request.form.get('id')
    i = Investor.query_one({'_id': _id})
    if i:
        try:
            i.remove()
        except Exception as e:
            return jsonify(status=500, reason=str(e))
        else:
            return jsonify(status=200, reason='')
    else:
        return jsonify(status=404, reason='投资人id={}未找到, 无法删除'.format(_id))


@user.route('/user/trade_account/')
@login_required
def trade_account():
    nav = 'accounts'
    tab = 'trade_account'
    investor = request.args.get('investor', '')
    exchange = request.args.get('exchange', '')
    add_investor = request.args.get('add_investor', '')
    add_exchange = request.args.get('add_exchange', '')
    bank = request.args.get('bank', '')
    investor = Investor.query_one({'_id': investor})
    exchange = Exchange.query_one({'abbr': exchange})
    user = current_user._id
    trade_accounts = TradeAccount.user_accounts(user)
    if investor:
        trade_accounts = [ta for ta in trade_accounts
                          if ta.investor == investor._id]
    if exchange:
        trade_accounts = [ta for ta in trade_accounts
                          if ta.exchange == exchange.abbr]
    if bank:
        trade_accounts = [ta for ta in trade_accounts
                          if ta.bank == bank]

    investors = Investor.user_investors(user)
    exchanges = sorted(list(Exchange.query()), key=lambda x: x.abbr)

    exchange_list = [{'text': e.abbr, 'value': e.abbr} for e in exchanges]
    investor_list = [{'text': i.name, 'value': i.name} for i in investors]

    investor_banks = {i.name: sorted([ba.bank for ba in i.bank_accounts])
                      for i in investors}
    exchange_banks = {conf['abbr']: sorted(conf['opening']['bank'])
                      for conf in CONFS}
    bank_exchanges = {}
    for ex, banks in exchange_banks.items():
        for b in banks:
            if b not in bank_exchanges:
                bank_exchanges[b] = []
            bank_exchanges[b].append(ex)
    investor_exchanges = {
        invesotr: sorted(set(sum(
            [bank_exchanges[b] for b in banks], [])))
        for invesotr, banks in investor_banks.items()
    }

    avail_investors = set(ta.investor for ta in trade_accounts)
    avail_exchanges = set(ta.exchange for ta in trade_accounts)
    avail_banks = set(ta.bank for ta in trade_accounts)
    investors = [i for i in investors if i._id in avail_investors]
    exchanges = [e for e in exchanges if e.abbr in avail_exchanges]

    thebanks = sorted(list(avail_banks))

    account_positions = {ta._id: sorted([p.to_dict() for p in ta.position],
                                        key=lambda p: p['symbol'])
                         for ta in trade_accounts}
    account_moneys = {ta._id: ta.money.to_dict() if ta.money else {}
                      for ta in trade_accounts}
    account_order_status = {ta._id: sorted([o.to_dict()
                                            for o in ta.order_status],
                                           key=lambda o: o['order'])
                            for ta in trade_accounts}
    account_orders = {ta._id: sorted([o.to_dict() for o in ta.orders],
                                     key=lambda o: o['symbol'])
                      for ta in trade_accounts}

    return render_template('user/trade_account.html', **locals())


@user.route('/user/trade_account/edit', methods=['POST'])
@login_required
def trade_account_edit():
    investor_name = request.form.get('investor')
    i = Investor.query_one({'name': investor_name})
    if not i:
        return jsonify(
            status=404,
            reason='投资人name={}未找到'.format(investor_name))
    user = current_user._id

    ta = {
        'user': user,
        'investor': i._id,
        'exchange': request.form.get('exchange'),
        'bank': request.form.get('bank'),
        'login_name': request.form.get('login_name'),
        'login_password': request.form.get('login_password'),
        'money_password': request.form.get('money_password'),
    }
    try:
        TradeAccount(ta).upsert()
    except Exception as e:
        TradeAccount.delete_one({'investor': ta['investor'],
                                 'exchange': ta['exchange']})
        try:
            TradeAccount(ta).upsert()
        except Exception as e:
            return jsonify(status=500, reason=str(e))

    return jsonify(status=200, reason='')


@user.route('/user/trade_account/delete', methods=['POST'])
@login_required
def trade_account_delete():
    ids = request.form.getlist('ids[]')
    try:
        TradeAccount.delete_many({'_id': {'$in': ids}})
    except Exception as e:
        return jsonify(status=500, reason=str(e))

    return jsonify(status=200, reason='')


@user.route('/user/trade_account/update', methods=['POST'])
@login_required
def trade_account_update():
    ids = request.form.getlist('ids[]')
    try:
        trade_accounts = TradeAccount.query({'_id': {'$in': ids}})
        for ta in trade_accounts:
            update_trade_account(ta)
    except Exception as e:
        return jsonify(status=500, reason=str(e))

    return jsonify(status=200, reason='')


@user.route('/user/trade_account/change_password', methods=['POST'])
@login_required
def trade_account_change_password():
    exchanges = request.form.getlist('exchanges[]')
    login_names = request.form.getlist('login_names[]')
    new_login_password = request.form.get('new_login_password')
    # TODO: add new_money_password support
    errors = []
    for ex, name in zip(exchanges, login_names):
        ta = TradeAccount.query_one({'exchange': ex,
                                     'login_name': name})
        pwd = ta.login_password
        print(ex, name, pwd)
        t = Trader(ex, name, pwd)
        print(new_login_password)
        t.change_password(new_login_password)
        if t.last_error:
            errors.append([ex, name, t.last_error])
        else:
            ta.login_password = new_login_password
            ta.upsert()
    if errors:
        return jsonify(status=500,
                       reason='部分账号修改失败',
                       details=errors)
    else:
        return jsonify(status=200, reason='')


@user.route('/user/trade_account/refresh_status', methods=['POST'])
@login_required
def trade_account_refresh_status():
    account_id = request.form.get('account_id')
    ta = TradeAccount.query_one({'_id': account_id})
    if ta:
        try:
            update_trade_account(ta)
        except Exception as e:
            return jsonify(status=500,
                           reason=str(e))

        return jsonify(status=200,
                       position=sorted([p.to_dict() for p in ta.position],
                                       key=lambda p: p['symbol']),
                       money=ta.money.to_dict(),
                       orders=sorted([o.to_dict() for o in ta.orders],
                                     key=lambda o: o['symbol']),
                       order_status=sorted([o.to_dict()
                                            for o in ta.order_status],
                                           key=lambda o: o['symbol']),
                       )
    else:
        return jsonify(status=500,
                       reason='账号未找到')


@user.route('/user/trade_account/update_quote', methods=['POST'])
@login_required
def trade_account_update_quote():
    account_id = request.form.get('account_id')
    symbol = request.form.get('symbol')
    ta = TradeAccount.query_one({'_id': account_id})
    if ta:
        try:
            qd = quote_detail(ta, symbol)
        except Exception as e:
            return jsonify(status=500, reason=str(e))
        else:
            return jsonify(status=200,
                           price=qd['price'],
                           highest=qd['highest'],
                           lowest=qd['lowest'],
                           asks=qd['asks'],
                           bids=qd['bids'])
    else:
        return jsonify(status=500, reason='账号未找到')


@user.route('/user/trade_account/order', methods=['POST'])
@login_required
def trade_account_order():
    account_id = request.form.get('account_id')
    ta = TradeAccount.query_one({'_id': account_id})
    if ta:
        type_ = request.form.get('type_')
        symbol = request.form.get('symbol')
        price = float(request.form.get('price'))
        quantity = int(request.form.get('quantity'))
        try:
            r, err = order(ta, type_, symbol, price, quantity)
        except Exception as e:
            return jsonify(status=500, reason=str(e))
        else:
            if r:
                return jsonify(status=200, reason='下单成功')
            else:
                return jsonify(status=400, reason=err)
    else:
        return jsonify(status=500, reason='账号未找到')


@user.route('/user/trade_account/withdraw', methods=['POST'])
@login_required
def trade_account_withdraw():
    account_id = request.form.get('account_id')
    order = request.form.get('order')
    ta = TradeAccount.query_one({'_id': account_id})
    if ta:
        try:
            r, err = withdraw(ta, order)
        except Exception as e:
            return jsonify(status=500, reason=str(e))
        else:
            if r:
                return jsonify(status=200, reason='撤单成功')
            else:
                return jsonify(status=400, reason=err)
    else:
        return jsonify(status=500, reason='账号未找到')


@user.route('/user/trade_account/transfer', methods=['POST'])
@login_required
def trade_account_transfer():
    account_id = request.form.get('account_id')
    inout = request.form.get('inout')
    amount = float(request.form.get('amount') or 0)
    ta = TradeAccount.query_one({'_id': account_id})
    if ta:
        try:
            r, err = transfer(ta, inout, amount)
        except Exception as e:
            return jsonify(status=500, reason=str(e))
        else:
            if r:
                return jsonify(status=200, reason='出入金已提交')
            else:
                return jsonify(status=400, reason=err)
    else:
        return jsonify(status=500, reason='账号未找到')
