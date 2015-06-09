from flask import render_template
from flask.ext.login import login_required

from ybk.user import admin_required

from .views import admin


@admin.route('/admin/')
@admin_required
def index():
    nav = 'index'
    return render_template('admin/index.html', **locals())
