from datetime import datetime, timedelta
from distutils.util import strtobool

import flask_login
from dateutil import parser
from dateutil.tz import UTC
from flask import Blueprint, render_template, request, jsonify
from flask_login import login_manager, LoginManager
from togger import application
from togger.event import event_api
from togger.event.models import Event

bp = Blueprint("event", __name__, template_folder="templates")
login_manager = LoginManager()


@application.route('/report', methods=['GET'])
@flask_login.login_required
def render_report():
    start_str = request.args.get('start')
    if not start_str:
        start_str = datetime.today().strftime('%d-%m-%Y')
    start = parser.parse(start_str, dayfirst=True).astimezone(UTC)
    end_str = request.args.get('end')
    if not end_str:
        end_str = datetime.today().strftime('%d-%m-%Y')
    end = (parser.parse(end_str, dayfirst=True) + timedelta(days=1)).astimezone(UTC)
    report = event_api.get_report(start=start, end=end)
    return render_template('report.html', report=report, start=start_str, end=end_str)


@application.route('/get_events', methods=['GET'])
@flask_login.login_required
def get_events():
    start = parser.isoparse(request.args.get('start')).astimezone(UTC)
    end = parser.isoparse(request.args.get('end')).astimezone(UTC)
    events = [event.serialized for event in event_api.get_events(start, end)]
    return jsonify(events)


@application.route('/render_shifts', methods=['GET'])
@flask_login.login_required
def render_shifts():
    event_id = request.args.get('id')
    is_editable = bool(strtobool(request.args.get('isEditable')))
    event = event_api.get_event(event_id)
    return render_template('shifts_modal.html', is_editable=is_editable,
                           event=event)


@application.route('/render_event', methods=['GET'])
@flask_login.login_required
def render_event():
    if request.args.get('id'):
        event = event_api.get_event(request.args.get('id'))
    else:
        event = Event(id="", title="", start=request.args.get('startDateTime'), end=request.args.get('endDateTime'),
                      all_day=request.args.get('allDay'))
    return render_template('event_modal.html', event=event)


@application.route('/post_event', methods=['POST'])
@flask_login.login_required
def post_event(all_day=False, event_id=None, recurrent=False):
    start = parser.parse(request.form['startDateTime'])
    end = parser.parse(request.form['endDateTime'])
    title = request.form['eventTitle']
    description = request.form['eventDescription']
    if 'isRecurrent' in request.form:
        recurrent = request.form['isRecurrent']
    if 'allDay' in request.form:
        all_day = bool(strtobool(request.form['allDay']))
    if 'eventId' in request.form and request.form['eventId']:
        event_id = request.form['eventId']
    event_api.save_event(title=title, description=description, start=start, end=end, all_day=all_day,
                         event_id=event_id, recurrent=recurrent)
    return '', 204


@application.route('/remove_event', methods=['POST'])
@flask_login.login_required
def remove_event():
    event_id = request.form['eventId']
    event_api.remove_event(event_id)
    return '', 204


@application.route('/post_shifts', methods=['POST'])
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
    event_api.save_shift(event_id=event_id, new_person_name=person_name, shift_ids_to_remove=shift_ids_to_remove)
    return '', 204


@bp.record_once
def on_load(state):
    login_manager.init_app(state.app)
