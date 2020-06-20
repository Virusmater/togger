import uuid
from datetime import date, timedelta, datetime

from flask_login import UserMixin
from itsdangerous import URLSafeSerializer, BadSignature
from sqlalchemy import UniqueConstraint
from werkzeug.security import generate_password_hash, check_password_hash

from togger import db
from togger.database import GUID


def _gen_valid_until():
    valid_until = date.today() + timedelta(days=2)
    return valid_until


class User(db.Model, UserMixin):
    auth_v = URLSafeSerializer(db.app.config['SECRET_KEY'], "validate")
    auth_p = URLSafeSerializer(db.app.config['SECRET_KEY'], "password")

    id = db.Column(GUID(), primary_key=True, default=uuid.uuid4)
    alias_id = db.Column(GUID(), default=uuid.uuid4, nullable=False, unique=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    is_verified = db.Column(db.Boolean, default=False, nullable=False)
    roles = db.relationship('Role', backref='User', cascade="all,delete", lazy=True)

    def set_password(self, password):
        self.password = generate_password_hash(password)
        self.alias_id = uuid.uuid4()

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def generate_validate_token(self):
        return self.auth_v.dumps({"username": self.username, "valid_until": _gen_valid_until().strftime('%d-%m-%Y')})

    def check_validate_token(self, token):
        try:
            data = self.auth_v.loads(token)
        except BadSignature:
            return False
        self.username = data['username']
        return datetime.now() < datetime.strptime(data["valid_until"], '%d-%m-%Y')

    def generate_password_token(self):
        return self.auth_p.dumps({"username": self.username, "valid_until": _gen_valid_until().strftime('%d-%m-%Y')})

    def check_password_token(self, token):
        try:
            data = self.auth_p.loads(token)
        except BadSignature:
            return False
        self.username = data['username']
        return datetime.now() < datetime.strptime(data["valid_until"], '%d-%m-%Y')

    def get_id(self):
        return self.alias_id


class Role(db.Model):
    OWNER = 100
    MANAGER = 50
    USER = 10

    id = db.Column(GUID(), primary_key=True, default=uuid.uuid4)
    type = db.Column(db.Integer, nullable=False)
    calendar_id = db.Column(GUID(), db.ForeignKey('calendar.id'), nullable=False)
    calendar = db.relationship("Calendar")
    user_id = db.Column(GUID(), db.ForeignKey('user.id'), nullable=False)
    user = db.relationship("User")
    is_default = db.Column(db.Boolean, default=False, nullable=False)
    UniqueConstraint(calendar_id, user_id, name='role_cal_user_key')

    @property
    def can_edit_events(self):
        return int(self.type) >= Role.MANAGER
