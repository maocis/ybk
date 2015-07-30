from flask import render_template
from ybk.settings import CONFS
from ybk.models import Announcement

from .views import frontend


@frontend.route('/')
def index():
    nav = 'index'
    exchanges = CONFS
    announcements = [a for a in
                     Announcement.query()
                     .sort([('published_at', -1)])
                     .limit(len(exchanges))]
    for a in announcements:
        a.type_ = {
            'offer': '申购',
            'result': '中签',
            'stock': '托管',
        }.get(a.type_, '托管')
    return render_template('frontend/index.html', **locals())
