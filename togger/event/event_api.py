import flask_login
from dateutil.rrule import rrule, WEEKLY
from sqlalchemy import func

from togger import db
from .models import Shift, Event


def get_events(start, end, calendar_name="default"):
    calendar_id = flask_login.current_user.calendars[0].id
    events = Event.query.filter(Event.calendar_id == calendar_id).filter(Event.start >= start).filter(
        Event.end <= end).all()
    return events


def save_event(title, start, end, all_day=False, event_id=None, recurrent=False, calendar_name='default'):
    dates = [(start, end)]
    calendar_id = flask_login.current_user.calendars[0].id
    if recurrent:
        start_dates = (list(rrule(freq=WEEKLY, count=5, dtstart=start)))
        end_dates = (list(rrule(freq=WEEKLY, count=5, dtstart=end)))
        dates = list(zip(start_dates, end_dates))
    for start, end in dates:
        event = Event(title=title.strip(), start=start, end=end, all_day=all_day, id=event_id, calendar_id=calendar_id)
        db.session.merge(event)
    db.session.commit()


def remove_event(event_id):
    calendar_id = flask_login.current_user.calendars[0].id
    event = Event.query.filter(Event.id == event_id).filter(Event.calendar_id == calendar_id).first()
    db.session.delete(event)
    db.session.commit()


def get_event(event_id):
    calendar_id = flask_login.current_user.calendars[0].id
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
    calendar_id = flask_login.current_user.calendars[0].id
    report = db.session.query(Shift.person, func.count(Shift.person).label('total')) \
        .join(Event.shifts) \
        .filter(Event.calendar_id == calendar_id) \
        .filter(Event.start >= start) \
        .filter(Event.start < end) \
        .group_by(Shift.person).all()
    return report
