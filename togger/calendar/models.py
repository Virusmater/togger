import os
import uuid
from datetime import timedelta, date, datetime
from json import loads

from sqlalchemy import JSON
from togger import db
from togger.database import GUID
from itsdangerous import URLSafeSerializer


default_settings = "{\"firstDay\": \"1\"," \
                   " \"nextDayThreshold\": \"00:00:00\"," \
                   " \"scrollTime\": \"16:00:00\", " \
                   "\"slotMaxTime\": \"22:00:00\", " \
                   "\"slotMinTime\": \"09:00:00\"}"


class Calendar(db.Model):
    id = db.Column(GUID(), primary_key=True, default=uuid.uuid4)
    settings = db.Column(JSON, default=default_settings)
    name = db.Column(db.String(256), nullable=False)
    events = db.relationship('Event', backref='Calendar', cascade="all,delete", lazy=True)
    roles = db.relationship('Role', backref='Calendar', cascade="all,delete", lazy=True)

    def get_settings(self):
        return loads(self.settings)


def _gen_valid_until():
    valid_until = date.today() + timedelta(days=7)
    return valid_until


class Share:
    auth_s = URLSafeSerializer(os.environ.get("SECRET_KEY"), "share")

    def __init__(self, role_name=None, calendar_id=None, valid_until=_gen_valid_until(), token=None):
        if token:
            self._load_token(token=token)
        else:
            self.role_name = role_name
            self.calendar_id = calendar_id
            self.valid_until = valid_until

    def generate_token(self):
        return self.auth_s.dumps(
            {"role_name": self.role_name, "calendar_id": str(self.calendar_id), "valid_until": self.valid_until.strftime('%d-%m-%Y')})

    def _load_token(self, token):
        data = self.auth_s.loads(token)
        self.role_name = data["role_name"]
        self.calendar_id = uuid.UUID(data["calendar_id"])
        self.valid_until = datetime.strptime(data["valid_until"], '%d-%m-%Y')

    def is_valid(self):
        return datetime.now() < self.valid_until
