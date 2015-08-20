from flask import render_template, redirect
from flask.ext.login import login_required, current_user

from ybk.models import Investor, TradeAccount

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

    return render_template('user/personal_info.html', **locals())


@user.route('/user/investor_info/')
@login_required
def investor_info():
    nav = 'accounts'
    tab = 'investor_info'
    user = current_user._id
    investors = Investor.user_investors(user)
    return render_template('user/investor_info.html', **locals())


@user.route('/user/trade_account/')
@login_required
def trade_account():
    nav = 'accounts'
    tab = 'trade_account'
    return render_template('user/trade_account.html', **locals())
