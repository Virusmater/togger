import calendar
import math
from datetime import datetime, timedelta

from dateutil.rrule import rrulestr
from dateutil.tz import UTC
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from togger import db
from togger.calendar import calendar_dao
from .models import Shift, Event, RecurEvent
from ..auth import auth_dao
from ..auth.models import Role


def get_events(start, end):
    calendar_id = calendar_dao.get_current_calendar().id
    events = Event.query.filter(Event.calendar_id == calendar_id).filter(Event.start <= end).filter(
        Event.end >= start).all()
    recur_events_unboxed = list(filter(lambda event: event.recur_id is not None, events))
    events.extend(get_recur_events(start, end, recur_events_unboxed))
    events = list(filter(lambda event: event.hide is not True, events))
    return events


def get_recur_events(start, end, recur_events_unboxed):
    events = []
    calendar_id = calendar_dao.get_current_calendar().id
    recur_events = RecurEvent.query.filter(RecurEvent.calendar_id == calendar_id) \
        .filter(RecurEvent.start_recur <= end) \
        .filter((RecurEvent.end_recur >= start) | (RecurEvent.end_recur.is_(None))).all()
    for recur_event in recur_events:
        rrule = rrulestr(recur_event.rrule)
        if recur_event.end_recur:
            rrule = rrule.replace(until=recur_event.end_recur.replace(tzinfo=UTC))
        for start_date in list(rrule.between(after=start, before=end, inc=True)):
            start_date = start_date.astimezone(UTC).replace(tzinfo=None)
            # nasty part, do not add recurrent event if unboxed version already there
            # check if user moved the original event or changed it anyhow, e.g added shifts
            if not any(recur_event_unboxed.recur_id == recur_event.id and recur_event_unboxed.init_start == start_date
                       for recur_event_unboxed in recur_events_unboxed):
                duration = recur_event.end - recur_event.start
                event = generate_event(recur_event.id, start=start_date, end=start_date + duration)
                events.append(event)
    return events


@auth_dao.has_role(Role.MANAGER)
def save_event(title=None, description=None, start=None, end=None, all_day=False, event_id=None, recurrent=False,
               recurrent_interval=None,
               recur_id=None,
               init_start=None, timezone=None, event=None):
    calendar_id = calendar_dao.get_current_calendar().id
    if event:
        db.session.merge(event)
        db.session.commit()
    elif recurrent:
        save_group_event(title=title.strip(), description=description, start=start, end=end, all_day=all_day,
                         timezone=timezone, recurrent=recurrent, recurrent_interval=recurrent_interval)
    else:
        if not recur_id:
            recur_id = None
        event = Event(title=title.strip(), description=description,
                      start=start, end=end, all_day=all_day, id=event_id, calendar_id=calendar_id, recur_id=recur_id)
        if init_start:
            event.init_start = init_start
        db.session.merge(event)
        db.session.commit()


@auth_dao.has_role(Role.MANAGER)
def save_group_event(title=None, description=None, start=None, end=None, timezone=None, recurrent=None,
                     recurrent_interval=None, all_day=False, recur_id=None, init_start=None):
    calendar_id = calendar_dao.get_current_calendar().id
    if recur_id:
        # set end_recur for previous events
        recur_event = get_group_event(recur_id)
        if recur_event.calendar_id != calendar_id:
            return
        original_end_recur = None
        if recur_event.end_recur:
            original_end_recur = recur_event.end_recur
        recur_event.end_recur = init_start - timedelta(seconds=1)
        db.session.merge(recur_event)

        # generate new id and update rrule for new recurrent event
        rrule_str = get_common_rrule(start, timezone, recur_event.recurrent_type, recur_event.recurrent_interval)
        recur_event = RecurEvent(title=title.strip(), description=description,
                                 start=start, end=end, start_recur=start, end_recur=original_end_recur,
                                 all_day=all_day,
                                 calendar_id=calendar_id, rrule=rrule_str, recurrent_type=recur_event.recurrent_type,
                                 recurrent_interval=recur_event.recurrent_interval)

        # update init_date for all related events
        related_events = Event.query.filter(Event.recur_id == recur_id) \
            .filter(Event.calendar_id == recur_event.calendar_id) \
            .filter(Event.start >= start).all()
        for event in related_events:
            event.init_start = datetime.combine(event.init_start.replace(tzinfo=UTC).astimezone(timezone).date(),
                                                start.replace(tzinfo=UTC).astimezone(timezone).timetz()) \
                .astimezone(UTC).replace(tzinfo=None)
            event.recur_event = recur_event
            db.session.merge(event)
    else:
        rrule_str = get_common_rrule(start, timezone, recurrent, recurrent_interval)
        recur_event = RecurEvent(title=title.strip(), description=description,
                                 start=start, end=end, start_recur=start, all_day=all_day,
                                 calendar_id=calendar_id, rrule=rrule_str, recurrent_type=recurrent,
                                 recurrent_interval=recurrent_interval)
    db.session.merge(recur_event)
    db.session.commit()


@auth_dao.has_role(Role.MANAGER)
def remove_event(event_id):
    calendar_id = calendar_dao.get_current_calendar().id
    event = Event.query.filter(Event.id == event_id).filter(Event.calendar_id == calendar_id).first()
    if event.recur_id:
        event.hide = True
        for shift in shifts:
            db.session.delete(shift)
        db.session.merge(event)
    else:
        db.session.delete(event)
    db.session.commit()


@auth_dao.has_role(Role.MANAGER)
def remove_group_event(recur_id, start):
    recur_event = get_group_event(recur_id)
    recur_event.end_recur = start - timedelta(seconds=1)
    db.session.merge(recur_event)
    db.session.commit()


def get_event(event_id):
    calendar_id = calendar_dao.get_current_calendar().id
    return Event.query.filter(Event.id == event_id).filter(Event.calendar_id == calendar_id).first()


def get_group_event(recur_id):
    calendar_id = calendar_dao.get_current_calendar().id
    return RecurEvent.query.filter(RecurEvent.id == recur_id).filter(RecurEvent.calendar_id == calendar_id).first()


def generate_event(recur_id, start, end):
    recur_event = get_group_event(recur_id)
    event = Event(title=recur_event.title, description=recur_event.description,
                  start=start, end=end, all_day=recur_event.all_day, calendar_id=recur_event.calendar_id,
                  recur_id=recur_event.id)
    return event


def save_shift(event_id=None, new_person_name=None, shift_ids_to_remove=[], recur_id=None, start=None, end=None):
    if event_id:
        event = get_event(event_id)
    else:
        event = generate_event(recur_id=recur_id, start=start, end=end)
    for shift_id in shift_ids_to_remove:
        for shift in event.shifts:
            if str(shift.id) == shift_id:
                Shift.query.filter(Shift.id == shift_id).delete()
    if new_person_name:
        shift = Shift(person=new_person_name.strip(), event_id=event_id)
        event.shifts.append(shift)
    try:
        db.session.merge(event)
    except IntegrityError:
        return False
    db.session.commit()
    return True


@auth_dao.has_role(Role.MANAGER)
def get_report(start, end, calendar_name="default"):
    if calendar_dao.get_current_calendar():
        calendar_id = calendar_dao.get_current_calendar().id
        report = db.session.query(Shift.person, func.count(Shift.person).label('total')) \
            .join(Event.shifts) \
            .filter(Event.calendar_id == calendar_id) \
            .filter(Event.start <= end) \
            .filter(Event.end >= start) \
            .group_by(Shift.person).all()
        return report
    else:
        return None


def get_weekday(date, timezone):
    weekday = date.astimezone(timezone).weekday()
    return weekday, calendar.day_name[weekday]


def get_date(date, timezone):
    return date.astimezone(timezone).strftime('%B %d')


def get_weekday_occurrence(date, timezone):
    date_suffix = ["th", "st", "nd", "rd"]
    weekday_occurrence = math.ceil(date.astimezone(timezone).day / 7)
    if weekday_occurrence in [1, 2, 3]:
        return weekday_occurrence, "{weekday_occurrence}{date_suffix}" \
            .format(weekday_occurrence=weekday_occurrence, date_suffix=date_suffix[weekday_occurrence])
    else:
        return weekday_occurrence, "{weekday_occurrence}{date_suffix}" \
            .format(weekday_occurrence=weekday_occurrence, date_suffix=date_suffix[0])


def get_common_rrule(date, timezone, recurrent, recurrent_interval=0):
    rrule_str = "RRULE:INTERVAL={recurrent_interval};".format(recurrent_interval=recurrent_interval)
    if recurrent == 'daily':
        rrule_str += "FREQ=DAILY;WKST=MO"
    elif recurrent == 'weekly':
        weekday = get_weekday(date, timezone)[1]
        rrule_str += "FREQ=WEEKLY;WKST=MO;BYDAY={byday}".format(byday=weekday[0:2].upper())
    elif recurrent == 'monthly':
        weekday = get_weekday(date, timezone)[1]
        rrule_str += "FREQ=MONTHLY;WKST=MO;BYDAY={byday};BYMONTHDAY={bymonthday}".format(
            byday=weekday[0:2].upper(),
            bymonthday=_get_monthly_days(get_weekday_occurrence(date, timezone)[0]))
    elif recurrent == 'yearly':
        rrule_str += "FREQ=YEARLY;WKST=MO;BYMONTH={bymonth};BYMONTHDAY={bymonthday}".format(
            bymonth=date.astimezone(timezone).month, bymonthday=date.astimezone(timezone).day)
    elif recurrent == 'weekday':
        rrule_str += "FREQ=WEEKLY;WKST=MO;BYDAY=MO,TU,WE,TH,FR"
    dtstart = "DTSTART;TZID={timezone}:{iso_date}".format(
        timezone=timezone.zone, iso_date=date.astimezone(timezone).replace(tzinfo=None).isoformat())
    return "{dtstart}\n{rrule_str}".format(dtstart=dtstart, rrule_str=rrule_str)


# idea is from https://stackoverflow.com/questions/32402344/ical-rrule-for-second-week-of-january
def _get_monthly_days(occurance):
    if occurance == 1:
        return "1,2,3,4,5,6,7"
    elif occurance == 2:
        return "8,9,10,11,12,13,14"
    elif occurance == 3:
        return "15,16,17,18,19,20,21"
    elif occurance == 4:
        return "22,23,24,25,26,27,28"
    elif occurance == 5:
        return "29,30,31"
