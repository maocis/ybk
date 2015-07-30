from flask import render_template
from flask.ext.login import login_required

from .views import frontend


@frontend.route('/forum/')
@login_required
def forum():
    nav = 'forum'
    return render_template('frontend/forum.html', **locals())
