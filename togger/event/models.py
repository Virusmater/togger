from togger import db
import uuid
from togger.database import GUID


class Event(db.Model):
    id = db.Column(GUID(), primary_key=True, default=uuid.uuid4)
    title = db.Column(db.String(80), nullable=False)
    start = db.Column(db.DateTime, nullable=False)
    end = db.Column(db.DateTime, nullable=False)
    all_day = db.Column(db.Boolean, default=False, nullable=False)
    shifts = db.relationship('Shift', backref='Event', cascade="all,delete", lazy=True)
    calendar_id = db.Column(GUID(), db.ForeignKey('calendar.id'), nullable=False)


    @property
    def serialized(self):
        return {
            'id': self.id,
            'title': self.title,
            'start': self.start.isoformat() + 'Z',
            'end': self.end.isoformat() + 'Z',
            'color': self.get_color(),
            'allDay': self.all_day
        }

    def get_color(self):
        if len(self.shifts) > 1:
            return "#88B04B"
        elif len(self.shifts) > 0:
            return "#E08119"
        else:
            return "#9F9C99"


class Shift(db.Model):
    id = db.Column(GUID(), primary_key=True, default=uuid.uuid4)
    person = db.Column(db.String(80), nullable=False)
    event_id = db.Column(GUID(), db.ForeignKey('event.id'), nullable=False)

    @property
    def serialized(self):
        return {
            'id': self.id,
            'person': self.person
        }