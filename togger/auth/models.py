import uuid
from datetime import date, timedelta, datetime

from flask_login import UserMixin
from itsdangerous import URLSafeSerializer
from sqlalchemy import UniqueConstraint
from werkzeug.security import generate_password_hash, check_password_hash

from togger import db
from togger.database import GUID


def _gen_valid_until():
    valid_until = date.today() + timedelta(days=2)
    return valid_until


class User(db.Model, UserMixin):
    auth_v = URLSafeSerializer(db.app.config['SECRET_KEY'], "validate")

    id = db.Column(GUID(), primary_key=True, default=uuid.uuid4)
    username = db.Column(db.String(80), nullable=False, unique=True)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    is_verified = db.Column(db.Boolean, default=False, nullable=False)
    roles = db.relationship('Role', backref='User', cascade="all,delete", lazy=True)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def generate_validate_token(self):
        return self.auth_v.dumps({"username": self.username, "valid_until": _gen_valid_until().strftime('%d-%m-%Y')})

    def check_validate_token(self, token):
        data = self.auth_v.loads(token)
        self.username = data['username']
        return datetime.now() < datetime.strptime(data["valid_until"], '%d-%m-%Y')


class Role(db.Model):
    id = db.Column(GUID(), primary_key=True, default=uuid.uuid4)
    type = db.Column(db.String(256), nullable=False)
    calendar_id = db.Column(GUID(), db.ForeignKey('calendar.id'), nullable=False)
    calendar = db.relationship("Calendar")
    user_id = db.Column(GUID(), db.ForeignKey('user.id'), nullable=False)
    user = db.relationship("User")
    is_default = db.Column(db.Boolean, default=False, nullable=False)
    UniqueConstraint(calendar_id, user_id, name='role_cal_user_key')

    @property
    def can_edit_events(self):
        return self.type == "manager"
