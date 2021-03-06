from flask import render_template
from flask.ext.login import login_required

from ybk.settings import CONFS
from ybk.models import Announcement

from .views import frontend


@frontend.route('/')
@login_required
def index():
    nav = 'index'
    exchanges = CONFS
    for e in exchanges:
        urls = e['offer']['index']
        if isinstance(urls, list):
            e['offer']['index_url'] = urls[0]
        else:
            e['offer']['index_url'] = urls
        urls = e['result']['index']
        if isinstance(urls, list):
            e['result']['index_url'] = urls[0]
        else:
            e['result']['index_url'] = urls
    announcements = [a for a in
                     Announcement.query(
                        sort=[('published_at', -1)],
                        limit=len(exchanges))]
    for a in announcements:
        a.type_ = {
            'offer': '申购',
            'result': '中签',
            'stock': '托管',
        }.get(a.type_, '托管')
    return render_template('frontend/index.html', **locals())
