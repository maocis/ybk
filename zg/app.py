#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging

from flask import Flask, render_template, request, jsonify

app = Flask(__name__)


@app.route('/')
def summary():
    return render_template('summary.html', **locals())


@app.route('/login/')
def login():
    return render_template('login.html', **locals())


@app.route('/admin/')
def admin():
    return render_template('admin.html', **locals())


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format='[%(asctime)s] %(name)s'
                               '<%(levelname)s> %(message)s')

    app.run(host='0.0.0.0', port=5101, threaded=True, debug=True)
