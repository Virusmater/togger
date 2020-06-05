import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

application = Flask(__name__)
application.config.from_object('togger.default_settings')
if os.environ.get("SECRET_KEY"):
    application.secret_key = os.environ.get("SECRET_KEY")
if os.environ.get("SQLALCHEMY_DATABASE_URI"):
    application.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("SQLALCHEMY_DATABASE_URI")
if os.environ.get("SQLALCHEMY_TRACK_MODIFICATIONS"):
    application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = os.environ.get("SQLALCHEMY_TRACK_MODIFICATIONS")
db = SQLAlchemy(application)

from .event import models
from .auth import models
from .calendar import models

db.create_all()
