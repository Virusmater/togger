from distutils.util import strtobool

import flask_login
import pytz
from dateutil import parser
from dateutil.tz import UTC
from flask import Blueprint, request, jsonify

from togger.event import event_dao

bp = Blueprint("event_api", __name__, url_prefix="/api/v1/calendars/events")


@bp.route('/', methods=['GET'])
@flask_login.login_required
def get_events():
    start = parser.isoparse(request.args.get('start')).astimezone(UTC)
    end = parser.isoparse(request.args.get('end')).astimezone(UTC)
    events = [event.serialized for event in event_dao.get_events(start, end)]
    return jsonify(events)


@bp.route('/', methods=['POST'])
@flask_login.login_required
def post_event(all_day=False, event_id=None, group_id=None, recurrent=None, description=None, init_start=None,
               timezone=None):
    start = parser.parse(request.form['startDateTime'])
    end = parser.parse(request.form['endDateTime'])
    title = request.form['eventTitle']
    if 'eventDescription' in request.form:
        description = request.form['eventDescription']
    if 'recurrent' in request.form:
        recurrent = request.form['recurrent']
    if 'allDay' in request.form:
        all_day = bool(strtobool(request.form['allDay']))
    if 'eventId' in request.form and request.form['eventId']:
        event_id = request.form['eventId']
    if 'groupId' in request.form:
        group_id = request.form['groupId']
    if group_id and not event_id:
        if 'initStartDateTime' in request.form:
            init_start = parser.parse(request.form['initStartDateTime'])
    if request.form['timeZone']:
        timezone = pytz.timezone(request.form['timeZone'])
    event_dao.save_event(title=title, description=description, start=start, end=end, all_day=all_day,
                         event_id=event_id, group_id=group_id, recurrent=recurrent, init_start=init_start,
                         timezone=timezone)
    return '', 204


@bp.route('/', methods=['DELETE'])
@flask_login.login_required
def delete_event():
    event_id = request.form['eventId']
    if event_id:
        event_dao.remove_event(event_id)
    else:
        group_id = request.form['groupId']
        event_dao.remove_group_event(group_id=group_id)
    return '', 204


@bp.route('/shifts', methods=['POST'])
@flask_login.login_required
def post_shift(person_name=None, event_id=None):
    if 'eventId' in request.form:
        event_id = request.form['eventId']
    group_id = request.form['groupId']
    start = parser.parse(request.form['startDateTime'])
    end = parser.parse(request.form['endDateTime'])
    if request.form['newNameText']:
        person_name = request.form['newNameText']
    shift_ids_to_remove = []
    for key in request.form.keys():
        if "CheckBox" in key and request.form[key] == "false":
            shift_id = key[13:]
            shift_ids_to_remove.append(shift_id)
    event_dao.save_shift(event_id=event_id, new_person_name=person_name, shift_ids_to_remove=shift_ids_to_remove,
                         group_id=group_id, start=start, end=end)
    return '', 204
