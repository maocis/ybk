#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, render_template


def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'ybk3284'
    return app

app = create_app()


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
