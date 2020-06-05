import uuid
from sqlalchemy import JSON
from togger import db
from togger.database import GUID

default_settings = "{\"firstDay\": \"1\"," \
                   " \"nextDayThreshold\": \"00:00:00\"," \
                   " \"scrollTime\": \"16:00:00\", " \
                   "\"slotMaxTime\": \"22:00:00\", " \
                   "\"slotMinTime\": \"09:00:00\"}"

class Calendar(db.Model):
    id = db.Column(GUID(), primary_key=True, default=uuid.uuid4)
    settings = db.Column(JSON, default=default_settings)
    name = db.Column(db.String(80), nullable=False)
    events = db.relationship('Event', backref='Calendar', cascade="all,delete", lazy=True)
    user_id = db.Column(GUID(), db.ForeignKey('user.id'), nullable=False)
