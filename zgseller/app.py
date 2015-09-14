#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging

from flask import Flask, render_template, request, jsonify
from flask.ext.basicauth import BasicAuth

from trademanager import TradeManager, tops, names

app = Flask(__name__)

app.config['BASIC_AUTH_USERNAME'] = 'ybk369'
app.config['BASIC_AUTH_PASSWORD'] = 'ybk888'

basic_auth = BasicAuth(app)
tm = TradeManager()


@app.route('/')
@basic_auth.required
def index():
    symbol = request.args.get('symbol', '100001')
    namedict = {i['username']: i['name'] for i in tm.investors}
    return render_template('index.html',
                           tops=tops,
                           names=names,
                           namedict=namedict,
                           symbol=symbol)


@app.route('/update.ajax')
def update():
    symbol = request.args.get('symbol', '100001')
    tm.sync(symbol)
    if symbol not in tm.prices:
        return jsonify(
            status=200,
            total_money=tm.get_money(),
            moneys=[(m[0].username, m[1]) for m in tm.moneys],
            total_quantity=0,
            quantities=[],
        )
    else:
        return jsonify(
            status=200,
            total_money=tm.get_money(),
            moneys=[(m[0].username, m[1]) for m in tm.moneys],
            total_quantity=tm.get_quantity(symbol),
            quantities=[(q[0].username, q[1])
                        for q in tm.position.get(symbol, [])],
            instant_quantities={
                'buy': tm.instant_buy_quantities(tm.prices[symbol]),
                'sell': tm.instant_sell_quantities(symbol),
            },
            quote=tm.quotes[symbol],
            pendings=tm.pendings[symbol],
            highest=tm.highests[symbol],
            lowest=tm.lowests[symbol],
        )


@app.route('/quote.ajax')
def quote():
    symbol = request.args.get('symbol', '100001')
    quote = tm.quote(symbol)
    return jsonify(status=200, quote=quote)


@app.route('/withdraw.ajax', methods=['POST'])
def withdraw():
    symbol = request.form.get('symbol', '100001')
    type_ = request.form.get('type_', 'buy')
    tm.withdraw_symbol(symbol, type_)
    return jsonify(status=200)


@app.route('/make_order.ajax', methods=['POST'])
def make_order():
    type_ = request.form.get('type_', 'sell')
    symbol = request.form.get('symbol', '100001')
    price = float(request.form.get('price'))
    quantity = int(request.form.get('quantity'))
    tm.order_symbol(type_, symbol, price, quantity)
    return jsonify(status=200)


@app.route('/log.ajax')
def log():
    return jsonify(status=200, logs=tm.logs)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format='[%(asctime)s] %(name)s'
                               '<%(levelname)s> %(message)s')

    app.run(host='0.0.0.0', port=5002, threaded=True, debug=False)
