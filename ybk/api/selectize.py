from flask import request, jsonify

from ybk.models import Collection
from .views import api


@api.route('/api/load_symbols/')
def load_symbols():
    exchange = request.args.get('exchange', '')
    query = request.args.get('query', '')
    cond = {'$or': [{'name': {'$regex': query}},
                    {'symbol': {'$regex': query}}]}
    if exchange:
        cond['exchange'] = exchange
    result = [
        {'text': '{}({})'.format(c.symbol, c.name),
         'value': c.symbol}  # '{}-{}'.format(c.symbol, c.name)}
        for c in Collection.find(
            cond,
            {'name': 1, 'symbol': 1})]
    return jsonify(result=result)
