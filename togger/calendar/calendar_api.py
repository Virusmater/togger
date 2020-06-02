import flask_login
from flask.json import dumps, loads

from togger import db


def save_settings(settings):
    calendar = flask_login.current_user.calendars[0]
    calendar.settings = dumps(settings)
    db.session.merge(calendar)
    db.session.commit()
    return True


def get_settings():
    calendar = flask_login.current_user.calendars[0]
    return loads(calendar.settings)
