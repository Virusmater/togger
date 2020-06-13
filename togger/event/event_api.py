from distutils.util import strtobool

import flask_login
from dateutil import parser
from dateutil.tz import UTC
from flask import Blueprint, request, url_for, jsonify
from werkzeug.utils import redirect
from togger.auth import auth_api
from togger.calendar import calendar_dao
from togger.event import event_dao

bp = Blueprint("event_api",  __name__, url_prefix="/api/v1/calendars/events")


@bp.route('/', methods=['GET'])
@flask_login.login_required
def get_events():
    start = parser.isoparse(request.args.get('start')).astimezone(UTC)
    end = parser.isoparse(request.args.get('end')).astimezone(UTC)
    events = [event.serialized for event in event_dao.get_events(start, end)]
    return jsonify(events)


@bp.route('/', methods=['POST'])
@flask_login.login_required
def post_event(all_day=False, event_id=None, recurrent=False, description=None):
    start = parser.parse(request.form['startDateTime'])
    end = parser.parse(request.form['endDateTime'])
    title = request.form['eventTitle']
    if 'eventDescription' in request.form:
        description = request.form['eventDescription']
    if 'isRecurrent' in request.form:
        recurrent = request.form['isRecurrent']
    if 'allDay' in request.form:
        all_day = bool(strtobool(request.form['allDay']))
    if 'eventId' in request.form and request.form['eventId']:
        event_id = request.form['eventId']
    event_dao.save_event(title=title, description=description, start=start, end=end, all_day=all_day,
                         event_id=event_id, recurrent=recurrent)
    return '', 204


@bp.route('/', methods=['DELETE'])
@flask_login.login_required
def delete_event():
    event_id = request.form['eventId']
    event_dao.remove_event(event_id)
    return '', 204


@bp.route('/shifts', methods=['POST'])
@flask_login.login_required
def post_shift(person_name=None):
    event_id = request.form['eventId']
    if request.form['newNameText']:
        person_name = request.form['newNameText']
    shift_ids_to_remove = []
    for key in request.form.keys():
        if "CheckBox" in key and request.form[key] == "false":
            shift_id = key[13:]
            shift_ids_to_remove.append(shift_id)
    event_dao.save_shift(event_id=event_id, new_person_name=person_name, shift_ids_to_remove=shift_ids_to_remove)
    return '', 204