from flask import render_template
from .views import frontend


@frontend.route('/walkthrough/')
def walkthrough():
    nav = 'walkthrough'
    return render_template('frontend/walkthrough.html', **locals())
