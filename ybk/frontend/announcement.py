from flask import render_template, request

from ybk.models import Exchange, Announcement
from ybk.utils import Pagination

from .views import frontend


@frontend.route('/announcement/')
def announcement():
    nav = 'announcement'
    type_ = request.args.get('type', '')
    exchange = request.args.get('exchange', '')
    page = int(request.args.get('page', 1) or 1)

    limit = 10
    skip = limit * (page - 1)

    cond = {}
    if type_:
        cond['type_'] = type_
    if exchange:
        cond['exchange'] = exchange

    total = Announcement.find(cond).count()
    pagination = Pagination(page, limit, total)
    exchanges = list(Exchange.find())
    announcements = list(
        Announcement.find(cond)
        .sort([('published_at', -1)])
        .skip(skip).limit(limit))
    for a in announcements:
        a.type_ = '申购' if a.type_ == 'offer' else '中签'

    return render_template('frontend/announcement.html', **locals())
