from flask import render_template
from .views import frontend


@frontend.route('/forum/')
def forum():
    nav = 'forum'
    return render_template('frontend/forum.html', **locals())
