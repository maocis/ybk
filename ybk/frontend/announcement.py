from flask import render_template, request
from werkzeug.contrib.atom import AtomFeed

from ybk.models import Exchange, Announcement
from ybk.utils import Pagination

from .views import frontend


@frontend.route('/announcement/')
def announcement():
    nav = 'announcement'
    type_ = request.args.get('type', '')
    typecn = '申购' if type_ == 'offer' else '中签'
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
        a.typecn = '申购' if a.type_ == 'offer' else '中签'

    try:
        updated_at = list(Exchange.find()
                          .sort([('updated_at', -1)])
                          .limit(1))[0].updated_at
    except:
        # 只有当数据库为空时才会这样
        updated_at = None

    return render_template('frontend/announcement.html', **locals())


@frontend.route('/announcement/feed.atom')
def announcement_feed():
    def bjdate(d):
        from datetime import timedelta
        return (d + timedelta(hours=8)).strftime('%Y年%m月%d日')

    type_ = request.args.get('type', '')
    typecn = '申购' if type_ == 'offer' else '中签'
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
        Announcement.find(cond)
        .sort([('published_at', -1)])
        .limit(20))

    for a in announcements:
        feed.add('{} {}'.format(bjdate(a.published_at), a.title.strip()),
                 '更多内容请点击标题连接',
                 content_type='text',
                 author=a.exchange,
                 url=a.url,
                 updated=a.published_at,
                 published=a.published_at)
    return feed.get_response()
