#!/usr/bin/python3
# -*- coding: utf-8 -*-

from flask import render_template
from app import app

from app.forms import SearchForm
from app.get_pong import get_pong

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    form = SearchForm()
    app.logger.info('Index page')
    return render_template("index.html", title='pong', form=form, pong=get_pong(form.search.data), version=app.config['VERSION'])