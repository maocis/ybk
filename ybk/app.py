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
    nav = 'index'
    return render_template('index.html', **locals())


@app.route('/walkthrough/')
def walkthrough():
    nav = 'walkthrough'
    return render_template('walkthrough.html', **locals())


@app.route('/announcement/')
def announcement():
    nav = 'announcement'
    return render_template('announcement.html', **locals())


@app.route('/analysis/')
def analysis():
    nav = 'analysis'
    return render_template('analysis.html', **locals())


@app.route('/trade/')
def trade():
    nav = 'trade'
    return render_template('trade.html', **locals())


@app.route('/forum/')
def forum():
    nav = 'forum'
    return render_template('forum.html', **locals())


@app.route('/about/')
def about():
    nav = 'about'
    return render_template('about.html', **locals())

if __name__ == '__main__':
    app.run(debug=True)
