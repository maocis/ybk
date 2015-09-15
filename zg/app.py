#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging

from flask import Flask, render_template, request, jsonify
from flask.ext.basicauth import BasicAuth


app = Flask(__name__)
app.config['BASIC_AUTH_USERNAME'] = 'ybk369'
app.config['BASIC_AUTH_PASSWORD'] = 'ybk888'

basic_auth = BasicAuth(app)


@app.route('/')
def summary():
    return render_template('summary.html', **locals())


@app.route('/login/')
def login():
    return render_template('login.html', **locals())


@app.route('/admin/')
@basic_auth.required
def admin():
    return render_template('admin.html', **locals())


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format='[%(asctime)s] %(name)s'
                               '<%(levelname)s> %(message)s')

    app.run(host='0.0.0.0', port=5101, threaded=True, debug=True)
