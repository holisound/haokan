# -*- coding: utf-8 -*-
import logging
import os
import sys
import socket

DB_NAME = 'haokan'
DB_PASSWD = 'agfva2fu'

PRODUCTION = True
SECRET_KEY = "f73f01b9febf411a8f709f2dd496e563"

SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_DATABASE_URI_PREFIX = 'mysql+mysqldb://{user}:{passwd}@0.0.0.0/'.format(user=DB_NAME,passwd=DB_PASSWD)
SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI_PREFIX +'%s?charset=utf8' % DB_NAME


