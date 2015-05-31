from flask import render_template
from .views import frontend


@frontend.route('/analysis/')
def analysis():
    nav = 'analysis'
    return render_template('frontend/analysis.html', **locals())
