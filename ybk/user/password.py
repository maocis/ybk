from flask import render_template, request, jsonify

from ybk.models import User, Code
from .views import user


@user.route('/user/change_password/')
def change_password():
    return render_template('user/change_password.html', **locals())


@user.route('/user/change_password_success')
def change_password_success():
    return render_template('user/change_password_success.html', **locals())


@user.route('/user/change_password/submit', methods=['POST'])
def change_password_submit():
    mobile = request.form.get('mobile')
    password = request.form.get('password')
    code = request.form.get('code', '')
    v, reason = Code.verify(mobile, code)
    if v:
        try:
            u = User.query_one({'mobile': mobile})
            u.change_password(password)
        except Exception as e:
            return jsonify(status=500, reason=str(e))
        return jsonify(status=200)
    else:
        return jsonify(status=400, reason=reason)
