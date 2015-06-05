from flask import render_template
from ybk.settings import CONFS
from ybk.models import Announcement

from .views import frontend


@frontend.route('/')
def index():
    nav = 'index'
    exchanges = CONFS
    announcements = [a for a in
                     Announcement.find()
                     .sort([('published_at', -1)])
                     .limit(len(exchanges))]
    for a in announcements:
        a.type_ = '申购' if a.type_ == 'offer' else '中签'
    return render_template('frontend/index.html', **locals())
