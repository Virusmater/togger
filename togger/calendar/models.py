import uuid
from sqlalchemy import JSON
from togger import db
from togger.database import GUID


class Calendar(db.Model):
    id = db.Column(GUID(), primary_key=True, default=uuid.uuid4)
    settings = db.Column(JSON)
    name = db.Column(db.String(80), nullable=False)
    events = db.relationship('Event', backref='Calendar', cascade="all,delete", lazy=True)
    user_id = db.Column(GUID(), db.ForeignKey('user.id'), nullable=False)
