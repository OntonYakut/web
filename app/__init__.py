#!/usr/bin/python
#encoding = utf8

from flask import Flask


app = Flask(__name__)
app.config.from_object('config')
from momentjs import momentjs
app.jinja_env.globals['momentjs'] = momentjs

from app import views