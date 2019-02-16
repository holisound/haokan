# coding:utf-8
import os

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy import not_
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import config

db = SQLAlchemy()
# Define models


class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phonenumber = db.Column(db.String(32))
    args = db.Column(db.Text)
    headers = db.Column(db.Text)
    forms = db.Column(db.Text)
    createtime = db.Column(db.DateTime, default=datetime.now)    


def init_app(app):
    engine = create_engine(config.SQLALCHEMY_DATABASE_URI_PREFIX)
    DB_Session = sessionmaker(bind=engine)
    session = DB_Session()

    try:
        session.execute("USE %s" % config.DB_NAME)
    except Exception as e:
        if 'Unknown database' in e.message:
            # init database
            session.execute("""
                CREATE DATABASE IF NOT EXISTS %s DEFAULT CHARACTER 
                SET utf8 DEFAULT COLLATE utf8_general_ci
            """ % config.DB_NAME)
            session.commit()
            with app.app_context():
                db.drop_all()
                db.create_all()