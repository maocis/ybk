import json
import html
from datetime import datetime

from flask import render_template, request, redirect, url_for, jsonify

from ybk.user import admin_required
from ybk.models import Announcement, Collection

from .views import admin


@admin.route('/admin/parse/')
@admin_required
def parse():
    nav = 'parse'
    url = request.args.get('url')
    num_parsed = Announcement.find({'parsed': True}).count()
    num_total = Announcement.find().count()
    if url:
        announcement = Announcement.find_one({'url': url})
        colls = list(Collection.find({'from_url': url}))
        for coll in colls:
            if coll.offers_at:
                coll.offers_at = coll.offers_at.strftime('%Y%m%d')
            if coll.offer_cash_ratio:
                coll.offer_cash_ratio = '{:2.0f}%'.format(
                    coll.offer_cash_ratio * 100)
            if coll.offer_price:
                coll.offer_price = str(coll.offer_price)
                if coll.offer_price.endswith('.0'):
                    coll.offer_price = coll.offer_price[:-2]
    all_done = num_parsed == num_total
    return render_template('admin/parse.html', **locals())


@admin.route('/admin/parse/findone')
@admin_required
def parse_findone():
    announcement = Announcement.find_one({'parsed': False},
                                         sort=[('published_at', -1)])
    if announcement:
        return redirect(url_for('admin.parse', url=announcement.url))
    else:
        return redirect(url_for('admin.parse'))


@admin.route('/admin/parse/save', methods=['POST'])
@admin_required
def parse_save():
    exchange = request.form.get('exchange')
    status = request.form.get('status', '申购中')
    from_url = request.form.get('from_url')
    type_ = request.form.get('type')
    result = json.loads(request.form.get('result', []))

    if not exchange:
        return jsonify(status=500, reason="字段不全")

    from_url = html.unescape(from_url)
    if from_url:
        Collection.remove({'from_url': from_url})

    if type_ == 'offer':
        for coll in result:
            coll['exchange'] = exchange
            coll['status'] = status
            coll['from_url'] = from_url
            coll['offer_quantity'] = int(coll['offer_quantity'])
            coll['offer_price'] = float(coll['offer_price'])
            coll['offers_at'] = datetime.strptime(coll['offers_at'],
                                                  '%Y%m%d')
            coll['offer_cash_ratio'] = int(
                coll['offer_cash_ratio'].replace('%', '')) / 100.
            Collection(coll).upsert()

        Announcement.find_one({'_id': from_url}).update(
            {'$set': {'parsed': True}})
    elif type_ == 'result':
        for coll in result:
            coll['exchange'] = exchange
            coll['status'] = status
            coll['from_url'] = from_url
            if coll.get('invest_cash'):
                coll['invest_cash'] = float(coll['invest_cash'])
            else:
                del coll['invest_cash']
            if coll.get('invest_cash_return_ratio'):
                coll['invest_cash_return_ratio'] = float(
                    coll['invest_cash_return_ratio'].replace('%', '')) / 100.
            else:
                del coll['invest_cash_return_ratio']
            Collection(coll).upsert()

        Announcement.find_one({'_id': from_url}).update(
            {'$set': {'parsed': True}})
    return jsonify(status=200)


@admin.route('/admin/parse/remove', methods=['POST'])
@admin_required
def parse_remove():
    _id = request.form.get('_id')
    Announcement.remove({'_id': _id})
    return jsonify(status=200)
