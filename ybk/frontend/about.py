from flask import render_template
from .views import frontend


@frontend.route('/about/')
def about():
    nav = 'about'
    return render_template('frontend/about.html', **locals())
