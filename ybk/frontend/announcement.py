from flask import render_template
from .views import frontend


@frontend.route('/announcement/')
def announcement():
    nav = 'announcement'
    return render_template('frontend/announcement.html', **locals())
