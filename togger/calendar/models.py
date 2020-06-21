import uuid
from datetime import timedelta, date, datetime
from json import loads

from itsdangerous import URLSafeSerializer, BadSignature
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
    name = db.Column(db.String(256), nullable=False)
    events = db.relationship('Event', backref='Calendar', cascade="all,delete", lazy=True)
    roles = db.relationship('Role', backref='Calendar', cascade="all,delete", lazy=True)

    def get_settings(self):
        return loads(self.settings)


def _gen_valid_until():
    valid_until = date.today() + timedelta(days=7)
    return valid_until


class Share:
    auth_s = URLSafeSerializer(db.app.config['SECRET_KEY'], "share")

    def __init__(self, role_type=None, calendar_id=None, token=None):
        if token:
            self._load_token(token=token)
        else:
            self.role_type = role_type
            self.calendar_id = calendar_id
            self.valid_until = _gen_valid_until()

    def generate_token(self):
        return self.auth_s.dumps(
            {"role_type": self.role_type, "calendar_id": str(self.calendar_id),
             "valid_until": self.valid_until.strftime('%d-%m-%Y')})

    def _load_token(self, token):
        try:
            data = self.auth_s.loads(token)
            self.role_type = int(data["role_type"])
            self.calendar_id = uuid.UUID(data["calendar_id"])
            self.valid_until = datetime.strptime(data["valid_until"], '%d-%m-%Y')
        except BadSignature:
            return False

    def is_valid(self):
        return self.valid_until and datetime.now() < self.valid_until
