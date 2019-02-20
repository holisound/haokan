#!/usr/bin/env python
from flask import Flask
import src.haokan.api
import util


def make_app(debug=False, **kwargs):
    app = Flask(__name__)
    app.config.from_pyfile('config.py')
    app.debug = not app.config['PRODUCTION']
    app.jinja_env.auto_reload = app.debug
    app.jinja_env.globals.update(**kwargs)
    app.permanent_session_lifetime = 30 * 24 * 3600  # session live for seconds
    return app


app = make_app()
app.register_blueprint(src.haokan.api.app, url_prefix="/haokan/api")
util.init_app(app)
