from flask_login import UserMixin
from sqlalchemy import UniqueConstraint
from werkzeug.security import generate_password_hash, check_password_hash

from togger import db

import uuid

from togger.database import GUID


class User(db.Model, UserMixin):
    id = db.Column(GUID(), primary_key=True, default=uuid.uuid4)
    username = db.Column(db.String(80), nullable=False, unique=True)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    roles = db.relationship('Role', backref='User', cascade="all,delete", lazy=True)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


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
