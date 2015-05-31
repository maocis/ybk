from flask import render_template
from .views import frontend


@frontend.route('/')
def index():
    nav = 'index'
    return render_template('frontend/index.html', **locals())
