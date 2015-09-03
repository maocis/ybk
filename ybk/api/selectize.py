from flask import request, jsonify

from ybk.models import Collection
from .views import api


@api.route('/api/load_symbols/')
def load_symbols():
    exchange = request.args.get('exchange', '')
    query = request.args.get('query', '')
    exclude = request.args.get('exclude', '')
    cond = {'$or': [{'name': {'$regex': query}},
                    {'symbol': {'$regex': query}}]}
    if exchange:
        cond['exchange'] = exchange
    result = [
        {'text': '{}({})'.format(c.symbol, c.name),
         'value': c.symbol}  # '{}-{}'.format(c.symbol, c.name)}
        for c in Collection.query(
            cond,
            {'name': 1, 'symbol': 1})]
    if exclude:
        result = [r for r in result if exclude not in r['text']]
    return jsonify(result=result)
