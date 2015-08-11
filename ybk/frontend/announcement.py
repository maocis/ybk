from flask import render_template, request
from werkzeug.contrib.atom import AtomFeed

from ybk.models import Exchange, Announcement
from ybk.utils import Pagination

from .views import frontend


def type_to_cn(type_):
    return {
        'offer': '申购',
        'result': '中签',
        'stock': '托管',
    }.get(type_, '托管')


@frontend.route('/announcement/')
def announcement():
    locals()['type_to_cn'] = type_to_cn
    nav = 'announcement'
    tab = 'raw'
    type_ = request.args.get('type', '')
    typecn = type_to_cn(type_)
    exchange = request.args.get('exchange', '')
    page = int(request.args.get('page', 1) or 1)

    limit = 50
    skip = limit * (page - 1)

    cond = {}
    if type_:
        cond['type_'] = type_
    if exchange:
        cond['exchange'] = exchange

    total = Announcement.count(cond)
    pagination = Pagination(page, limit, total)
    exchanges = list(sorted(list(e.abbr for e in Exchange.query())))
    types = ['offer', 'result', 'stock']
    announcements = list(
        Announcement.query(cond,
                           sort=[('updated_at', -1)],
                           skip=skip, limit=limit))
    for a in announcements:
        a.typecn = type_to_cn(a.type_)

    ex = Exchange.query_one(sort=[('updated_at', -1)])
    updated_at = None if not ex else ex.updated_at

    return render_template('frontend/announcement.html', **locals())


@frontend.route('/announcement/feed.atom')
def announcement_feed():
    def bjdate(d):
        from datetime import timedelta
        return (d + timedelta(hours=8)).strftime('%Y年%m月%d日')

    type_ = request.args.get('type', '')
    typecn = type_to_cn(type_)
    exchange = request.args.get('exchange', '')
    cond = {}
    feedtitle = '邮币卡公告聚合'
    if type_:
        cond['type_'] = type_
        feedtitle += ' - {}'.format(typecn)
    if exchange:
        cond['exchange'] = exchange
        feedtitle += ' - {}'.format(exchange)

    feed = AtomFeed(feedtitle,
                    feed_url=request.url,
                    url=request.url_root)

    announcements = list(
        Announcement.query(cond,
            sort=[('updated_at', -1)], limit=20))

    for a in announcements:
        feed.add('{} {}'.format(bjdate(a.published_at), a.title.strip()),
                 '更多内容请点击标题连接',
                 content_type='text',
                 author=a.exchange,
                 url=a.url,
                 updated=a.updated_at,
                 published=a.published_at)
    return feed.get_response()
