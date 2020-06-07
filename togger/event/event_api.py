import flask_login
from dateutil.rrule import rrule, WEEKLY
from sqlalchemy import func

from togger import db
from togger.calendar import calendar_api
from .models import Shift, Event
from ..auth import auth_api


def get_events(start, end, calendar_name="default"):
    calendar_id = calendar_api.get_current_calendar().id
    events = Event.query.filter(Event.calendar_id == calendar_id).filter(Event.start >= start).filter(
        Event.end <= end).all()
    return events


@auth_api.can_edit_events
def save_event(title, start, end, all_day=False, event_id=None, recurrent=False, calendar_name='default'):
    dates = [(start, end)]
    calendar_id = calendar_api.get_current_calendar().id
    if recurrent:
        start_dates = (list(rrule(freq=WEEKLY, count=5, dtstart=start)))
        end_dates = (list(rrule(freq=WEEKLY, count=5, dtstart=end)))
        dates = list(zip(start_dates, end_dates))
    for start, end in dates:
        event = Event(title=title.strip(), start=start, end=end, all_day=all_day, id=event_id, calendar_id=calendar_id)
        db.session.merge(event)
    db.session.commit()


@auth_api.can_edit_events
def remove_event(event_id):
    calendar_id = calendar_api.get_current_calendar().id
    event = Event.query.filter(Event.id == event_id).filter(Event.calendar_id == calendar_id).first()
    db.session.delete(event)
    db.session.commit()


def get_event(event_id):
    calendar_id = calendar_api.get_current_calendar().id
    return Event.query.filter(Event.id == event_id).filter(Event.calendar_id == calendar_id).first()


def save_shift(event_id, new_person_name, shift_ids_to_remove=[]):
    event = get_event(event_id)
    for shift_id in shift_ids_to_remove:
        for shift in event.shifts:
            if str(shift.id) == shift_id:
                Shift.query.filter(Shift.id == shift_id).delete()
    if new_person_name:
        shift = Shift(person=new_person_name.strip(), event_id=event_id)
        event.shifts.append(shift)
    db.session.merge(event)
    db.session.commit()


def get_report(start, end, calendar_name="default"):
    calendar_id = calendar_api.get_current_calendar().id
    report = db.session.query(Shift.person, func.count(Shift.person).label('total')) \
        .join(Event.shifts) \
        .filter(Event.calendar_id == calendar_id) \
        .filter(Event.start >= start) \
        .filter(Event.start < end) \
        .group_by(Shift.person).all()
    return report
