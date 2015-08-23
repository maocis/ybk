from flask import render_template

from .views import user


@user.route('/user/change_password/')
def change_password():
    return render_template('user/change_password.html', **locals())


@user.route('/user/change_password_success')
def change_password_success():
    return render_template('user/change_password_success.html', **locals())
