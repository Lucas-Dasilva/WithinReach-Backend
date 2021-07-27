import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    #SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:5829@localhost/WithinReachDb'
    #sqlite database is simply a file on our filesystem
    SQLALCHEMY_TRACK_MODIFICATIONS = False

