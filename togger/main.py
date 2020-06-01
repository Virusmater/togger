from distutils.util import strtobool
from dateutil import parser
import flask_login
from flask import request, render_template, jsonify, redirect
from togger import application
from togger.event import event_api
from .auth import auth
from .event.models import Event

application.register_blueprint(auth.bp)

@application.route('/')
@flask_login.login_required
def main():
    return render_template('main.html')


@application.route('/get_events', methods=['GET'])
def get_events():
    start = parser.parse(request.args.get('start'))
    end = parser.parse(request.args.get('end'))
    events = [event.serialized for event in event_api.get_events(start, end)]
    return jsonify(events)


@application.route('/render_shifts', methods=['GET'])
def render_shifts():
    event_id = request.args.get('id')
    is_editable = bool(strtobool(request.args.get('isEditable')))
    event = event_api.get_event(event_id)
    return render_template('shifts_modal.html', is_editable=is_editable,
                           event=event)


@application.route('/render_event', methods=['GET'])
def render_event():
    if request.args.get('id'):
        event = event_api.get_event(request.args.get('id'))
    else:
        event = Event(id="", title="", start=request.args.get('startDateTime'), end=request.args.get('endDateTime'),
                      all_day=request.args.get('allDay'))
    return render_template('event_modal.html', event=event)


@application.route('/post_event', methods=['POST'])
def post_event(all_day=False, event_id=None, recurrent=False):
    start = parser.parse(request.form['startDateTime'])
    end = parser.parse(request.form['endDateTime'])
    title = request.form['eventTitle']
    if 'isRecurrent' in request.form:
        recurrent = request.form['isRecurrent']
    if 'allDay' in request.form:
        all_day = bool(strtobool(request.form['allDay']))
    if 'eventId' in request.form and request.form['eventId']:
        event_id = request.form['eventId']
    event_api.save_event(title=title, start=start, end=end, all_day=all_day, event_id=event_id, recurrent=recurrent)
    return redirect("/")


@application.route('/remove_event', methods=['POST'])
def remove_event():
    event_id = request.form['eventId']
    event_api.remove_event(event_id)
    return redirect("/")


@application.route('/post_shifts', methods=['POST'])
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
    return redirect("/")
