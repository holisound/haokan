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
SQLALCHEMY_DATABASE_URI = 'mysql+mysqldb://root:{passwd}@0.0.0.0/'.format(passwd=DB_PASSWD)+'%s?charset=utf8' % DB_NAME


