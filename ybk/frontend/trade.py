from flask import render_template
from .views import frontend


@frontend.route('/trade/')
def trade():
    nav = 'trade'
    return render_template('frontend/trade.html', **locals())
