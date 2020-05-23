from tinydb import TinyDB, Query
from dateutil.rrule import rrule, WEEKLY

db = TinyDB("resources/togger.json")


def get_events():
    events = db.table('events').all()
    for event in events:
        shift = Query()
        event['id'] = event.doc_id
        shifts = db.table('shifts').search(shift.event_id == str(event.doc_id))
        if len(shifts) > 1:
            event['color'] = "#88B04B"
        elif len(shifts) > 0:
            event['color'] = "#E08119"
    return events


def save_event(title, start, end, all_day=False, event_id=None, recurrent=False):
    dates = [(start, end)]
    if recurrent:
        start_dates = (list(rrule(freq=WEEKLY, count=5, dtstart=start)))
        end_dates = (list(rrule(freq=WEEKLY, count=5, dtstart=end)))
        dates = list(zip(start_dates, end_dates))
    events_table = db.table('events')
    for start, end in dates:
        if event_id:
            events_table.update({"title": title,
                                 "start": str(start), "end": str(end),
                                 "allDay": all_day},
                                doc_ids=[int(event_id)])
        else:
            events_table.insert({"title": title,
                                 "start": str(start), "end": str(end),
                                 "allDay": all_day})


def remove_event(event_id):
    events_table = db.table('events')
    events_table.remove(doc_ids=[int(event_id)])


def get_event(event_id):
    events_table = db.table('events')
    return events_table.get(doc_id=int(event_id))


def get_shifts(event_id):
    shift = Query()
    shifts = db.table('shifts').search(shift.event_id == event_id)
    return shifts


def save_shift(event_id, new_person_name, shift_ids_to_remove=None):
    if shift_ids_to_remove is None:
        shift_ids_to_remove = []
    if new_person_name:
        db.table('shifts').insert({"event_id": event_id, "worker_name": new_person_name})
    for shift_id in shift_ids_to_remove:
        db.table('shifts').remove(doc_ids=[int(shift_id)])
