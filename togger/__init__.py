import os

from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_talisman import Talisman

csp = {
    'script-src': ['\'unsafe-inline\'', '\'self\'', 'code.jquery.com', 'cdn.jsdelivr.net',
                   'stackpath.bootstrapcdn.com', 'cdnjs.cloudflare.com']
}

application = Flask(__name__)
talisman = Talisman(application, content_security_policy=csp)
application.config.from_object('togger.default_settings')
if os.environ.get("SECRET_KEY"):
    application.secret_key = os.environ.get("SECRET_KEY")
if os.environ.get("SQLALCHEMY_DATABASE_URI"):
    application.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("SQLALCHEMY_DATABASE_URI")
if os.environ.get("SQLALCHEMY_TRACK_MODIFICATIONS"):
    application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = os.environ.get("SQLALCHEMY_TRACK_MODIFICATIONS")
if os.environ.get("SMTP_MAILBOX"):
    application.config['SMTP_MAILBOX'] = os.environ.get("SMTP_MAILBOX")
if os.environ.get("SMTP_LOGIN"):
    application.config['SMTP_LOGIN'] = os.environ.get("SMTP_LOGIN")
if os.environ.get("SMTP_PASSWORD"):
    application.config['SMTP_PASSWORD'] = os.environ.get("SMTP_PASSWORD")
if os.environ.get("SMTP_SERVER"):
    application.config['SMTP_SERVER'] = os.environ.get("SMTP_SERVER")
if os.environ.get("SMTP_PORT"):
    application.config['SMTP_PORT'] = os.environ.get("SMTP_PORT")
if os.environ.get("APP_URL"):
    application.config['APP_URL'] = os.environ.get("APP_URL")

db = SQLAlchemy(application)
migrate = Migrate(application, db)
