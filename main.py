#!/usr/bin/env python
from flask import Flask
# import src.xpit.api
# import src.auth.api
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
# app.register_blueprint(src.xpit.api.app, url_prefix="/p/xpit")
# app.register_blueprint(src.auth.api.app, url_prefix="/p/auth")
util.init_app(app)
