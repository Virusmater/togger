import flask_login
from dateutil.rrule import rrule, WEEKLY
from togger import db
from .models import Shift, Event


def get_events(start, end):
    user_id = flask_login.current_user.id
    events = Event.query.filter(Event.owner == user_id).filter(Event.start >= start).filter(Event.end <= end).all()
    return events


def save_event(title, start, end, all_day=False, event_id=None, recurrent=False):
    dates = [(start, end)]
    user_id = flask_login.current_user.id
    if recurrent:
        start_dates = (list(rrule(freq=WEEKLY, count=5, dtstart=start)))
        end_dates = (list(rrule(freq=WEEKLY, count=5, dtstart=end)))
        dates = list(zip(start_dates, end_dates))
    for start, end in dates:
        event = Event(title=title, start=start, end=end, all_day=all_day, owner=user_id, id=event_id)
        db.session.merge(event)
    db.session.commit()


def remove_event(event_id):
    user_id = flask_login.current_user.id
    event = Event.query.filter(Event.id == event_id).filter(Event.owner == user_id).first()
    db.session.delete(event)
    db.session.commit()


def get_event(event_id):
    user_id = flask_login.current_user.id
    return Event.query.filter(Event.id == event_id).filter(Event.owner == user_id).first()


def save_shift(event_id, new_person_name, shift_ids_to_remove=[]):
    event = get_event(event_id)
    for shift_id in shift_ids_to_remove:
        for shift in event.shifts:
            if str(shift.id) == shift_id:
                Shift.query.filter(Shift.id == shift_id).delete()
    if new_person_name:
        shift = Shift(person=new_person_name, event_id=event_id)
        event.shifts.append(shift)
    db.session.merge(event)
    db.session.commit()
