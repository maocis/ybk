#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import request, jsonify, current_app
import requests

from ybk.models import User, Code
from ybk.log import serve_log as log

from .views import api


@api.route('/api/send_code/', methods=['POST'])
def send_code():
    mobile = request.form.get('mobile')
    type_ = request.form.get('type')
    cc, reason = Code.can_create(mobile, type_)
    if not cc:
        return jsonify(status=400, reason=reason)
    else:
        c = Code.create_code(mobile)
        r = send_sms(c.mobile, c.text)
        if r['status'] != 200:
            c.delete()
        return jsonify(**r)


@api.route('/api/verify_code/', methods=['POST'])
def verify_code():
    mobile = request.form.get('mobile', '')
    code = request.form.get('code', '')
    v, reason = Code.verify(mobile, code)
    if v:
        return jsonify(status=200)
    else:
        return jsonify(status=400, reason=reason)


def send_sms_yunpian(mobile, text):
    log.info('向 {} 发送 "{}"'.format(mobile, text))
    url = 'http://yunpian.com/v1/sms/send.json'
    conf = current_app.config
    data = {
        'apikey': conf.get('yunpian_apikey', ''),
        'mobile': mobile,
        'text': text,
    }
    r = requests.post(url, data=data).json()
    log.info('...发送结果为 {}'.format(r))
    if r['code'] == 0:
        r['status'] = 200
    else:
        r['status'] = 500
    r['reason'] = r['msg']
    return r


send_sms = send_sms_yunpian
