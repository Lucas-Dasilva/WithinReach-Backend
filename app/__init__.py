from flask import Flask, session
from config import Config
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta
from flask_moment import Moment
from flask_login import LoginManager
from flask_cors import CORS

application = app = Flask(__name__)

ENV = 'prod'
if ENV == 'dev':
  app.debug = True
  app.config.from_object(Config)
else:
  app.debug = False
  app.config.from_object(Config)
  #sqlite database is simply a file on our filesystem
  SQLALCHEMY_TRACK_MODIFICATIONS = False

db = SQLAlchemy(app)
moment = Moment(app)
login = LoginManager(app)
login.login_view = 'login'
from app import routes, models, errors



