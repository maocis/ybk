from flask import render_template

from ybk.user import admin_required

from .views import admin


@admin.route('/admin/parse/')
@admin_required
def parse():
    nav = 'parse'
    return render_template('admin/parse.html', **locals())
