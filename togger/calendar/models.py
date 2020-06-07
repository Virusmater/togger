import uuid
from datetime import timedelta, date

from sqlalchemy import JSON
from togger import db
from togger.database import GUID

default_settings = "{\"firstDay\": \"1\"," \
                   " \"nextDayThreshold\": \"00:00:00\"," \
                   " \"scrollTime\": \"16:00:00\", " \
                   "\"slotMaxTime\": \"22:00:00\", " \
                   "\"slotMinTime\": \"09:00:00\"}"


def gen_valid_until():
    valid_until = date.today() + timedelta(days=7)
    return valid_until


class Calendar(db.Model):
    id = db.Column(GUID(), primary_key=True, default=uuid.uuid4)
    settings = db.Column(JSON, default=default_settings)
    name = db.Column(db.String(256), nullable=False)
    events = db.relationship('Event', backref='Calendar', cascade="all,delete", lazy=True)


class Share(db.Model):
    id = db.Column(GUID(), primary_key=True, default=uuid.uuid4)
    role_name = db.Column(db.String(256), nullable=False)
    valid_until = db.Column(db.DateTime, nullable=False, default=gen_valid_until)
    calendar_id = db.Column(GUID(), db.ForeignKey('calendar.id'), nullable=False)
    calendar = db.relationship("Calendar")
