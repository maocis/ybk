import json
import base64

from flask import render_template, redirect, request, jsonify
from flask.ext.login import login_required, current_user

from ybk.models import Investor, TradeAccount, Exchange

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
    investor = Investor.query_one({'_id': investor})
    exchange = Exchange.query_one({'abbr': exchange})
    user = current_user._id
    investors = Investor.user_investors(user)
    exchanges = sorted(list(Exchange.query()), key=lambda x: x.abbr)
    return render_template('user/trade_account.html', **locals())
