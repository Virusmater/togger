import os
from flask import Flask
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy

application = Flask(__name__)
load_dotenv()
application.secret_key = os.environ.get("SECRET_KEY")
application.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("SQLALCHEMY_DATABASE_URI")
application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = os.environ.get("SQLALCHEMY_TRACK_MODIFICATIONS")
db = SQLAlchemy(application)

from .event import models
from .auth import models
db.create_all()
