from flask import render_template

from ybk.user import admin_required

from .views import admin


@admin.route('/admin/about/')
@admin_required
def about():
    nav = 'about'
    return render_template('admin/about.html', **locals())
