import os
from distutils.util import strtobool
from dateutil import parser
import flask_login
from flask import Flask, request, render_template, jsonify, redirect
import event_api

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")

import auth

app.register_blueprint(auth.bp)


@app.route('/')
@flask_login.login_required
def main():
    return render_template('main.html')


@app.route('/get_events', methods=['GET'])
def get_events():
    return jsonify(event_api.get_events())


@app.route('/render_shifts', methods=['GET'])
def render_shifts():
    event_id = request.args.get('id')
    is_editable = bool(strtobool(request.args.get('isEditable')))
    event_title = event_api.get_event(event_id)['title']
    return render_template('shifts_modal.html', is_editable=is_editable,
                           event_title=event_title, shifts=event_api.get_shifts(event_id),
                           event_id=event_id)


@app.route('/render_event', methods=['GET'])
def render_event():
    start_date_time = request.args.get('startDateTime')
    end_date_time = request.args.get('endDateTime')
    all_day = request.args.get('allDay')
    return render_template('event_modal.html', start_date_time=start_date_time,
                           end_date_time=end_date_time, all_day=all_day)


@app.route('/post_event', methods=['POST'])
def post_event(all_day=False, event_id=None, recurrent=False):
    start = parser.parse(request.form['startDateTime'])
    end = parser.parse(request.form['endDateTime'])
    title = request.form['eventTitle']
    if 'isRecurrent' in request.form:
        recurrent = request.form['isRecurrent']
    if 'allDay' in request.form:
        all_day = bool(strtobool(request.form['allDay']))
    if 'eventId' in request.form:
        event_id = request.form['eventId']
    event_api.save_event(title=title, start=start, end=end, all_day=all_day, event_id=event_id, recurrent=recurrent)
    return redirect("/")


@app.route('/remove_event', methods=['POST'])
def remove_event():
    event_id = request.form['eventId']
    event_api.remove_event(event_id)
    return redirect("/")


@app.route('/post_shifts', methods=['POST'])
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
