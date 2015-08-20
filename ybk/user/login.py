import functools
from datetime import datetime

from flask import render_template, request, jsonify, redirect, current_app
from flask.ext.login import login_user, current_user, logout_user

from ybk.models import User, Code

from .views import user


def admin_required(func):
    @functools.wraps(func)
    def decorated_view(*args, **kwargs):
        if current_user.is_authenticated() and current_user.is_admin():
            return func(*args, **kwargs)
        else:
            return current_app.login_manager.unauthorized()
    return decorated_view


@user.route('/user/login/')
def login():
    next_url = request.args.get('next', '/')
    return render_template('user/login.html', **locals())


@user.route('/user/login/register.ajax', methods=['POST'])
def register():
    mobile = request.form.get('mobile', '')
    username = request.form.get('username', '')
    password = request.form.get('password', '')
    invited_by = request.form.get('invited_by', '')
    code = request.form.get('code', '')
    v, reason = Code.verify(mobile, code)
    if v:
        try:
            u = User.create_user(mobile, username, password, invited_by)
        except Exception as e:
            return jsonify(status=500, reason=str(e))
        else:
            u.activate()
        return jsonify(status=200)
    else:
        return jsonify(status=400, reason=reason)


@user.route('/user/register_success')
def register_success():
    return render_template('user/register_success.html', **locals())


@user.route('/user/login/check.ajax', methods=['POST'])
def check_login():
    if current_user.is_authenticated():
        return jsonify(status=200)

    mobile = request.form.get('mobile')
    password = request.form.get('password')
    remember = request.form.get('remember') == 'on'
    u = User.check_login(mobile, password)
    if u:
        login_user(u, remember=remember)
        u.last_login_at = datetime.utcnow()
        u.upsert()
        return jsonify(status=200, reason='')
    else:
        return jsonify(status=403, reason='用户名或密码错误')


@user.route('/user/logout/')
def logout():
    if current_user.is_authenticated():
        logout_user()
    next_url = request.args.get('next', '/')
    return redirect(next_url)
