from togger import db
from sqlalchemy.types import TypeDecorator, CHAR
from sqlalchemy.dialects.postgresql import UUID
import uuid


class GUID(TypeDecorator):
    """Platform-independent GUID type.

    Uses PostgreSQL's UUID type, otherwise uses
    CHAR(32), storing as stringified hex values.

    """
    impl = CHAR

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(UUID())
        else:
            return dialect.type_descriptor(CHAR(32))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                return "%.32x" % uuid.UUID(value).int
            else:
                # hexstring
                return "%.32x" % value.int

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            if not isinstance(value, uuid.UUID):
                value = uuid.UUID(value)
            return value


class Event(db.Model):
    id = db.Column(GUID(), primary_key=True, default=uuid.uuid4())
    title = db.Column(db.String(80), nullable=False)
    start = db.Column(db.DateTime, nullable=False)
    end = db.Column(db.DateTime, nullable=False)
    owner = db.Column(db.String(80), nullable=False)
    all_day = db.Column(db.Boolean, default=False, nullable=False)
    shifts = db.relationship('Shift', backref='Event', cascade="all,delete", lazy=True)

    @property
    def serialized(self):
        # shifts = [shift.serialized for shift in self.shifts]
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
    id = db.Column(GUID(), primary_key=True, default=uuid.uuid4())
    person = db.Column(db.String(80), nullable=False)
    event_id = db.Column(GUID(), db.ForeignKey('event.id'), nullable=False)

    @property
    def serialized(self):
        return {
            'id': self.id,
            'person': self.person
        }