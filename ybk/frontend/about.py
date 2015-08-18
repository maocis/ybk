from flask import render_template
from flask.ext.login import login_required

from .views import frontend


@frontend.route('/about/')
@login_required
def about():
    nav = 'about'
    return render_template('frontend/about.html', **locals())
