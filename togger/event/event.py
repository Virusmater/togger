from datetime import datetime, timedelta

import flask_login
import pytz
from dateutil import parser
from dateutil.tz import UTC
from flask import Blueprint, render_template, request
from flask_login import login_manager, LoginManager
from flask_wtf import FlaskForm

from togger import application
from togger.event import event_dao
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
    report = event_dao.get_report(start=start, end=end)
    return render_template('report.html', report=report, start=start_str, end=end_str)


@application.route('/render_shifts', methods=['GET'])
@flask_login.login_required
def render_shifts(time_zone=None):
    if request.args.get('timeZone'):
        time_zone = request.args.get('timeZone')
    event_id = request.args.get('id')
    if event_id:
        event = event_dao.get_event(event_id)
    else:
        recur_id = request.args.get('recurId')
        event = event_dao.generate_event(recur_id, start=request.args.get('start'),
                                         end=request.args.get('end'))
    return render_template('shifts_modal.html',
                           event=event, time_zone=time_zone, form=FlaskForm())


@application.route('/render_event', methods=['GET'])
@flask_login.login_required
def render_event(timezone=None, recur_event=None):
    if request.args.get('timeZone'):
        timezone = pytz.timezone(request.args.get('timeZone'))
    event_id = request.args.get('id')
    recur_id = request.args.get('recurId')

    if request.args.get('start'):
        start = parser.parse(request.args.get('start'))
    if request.args.get('end'):
        end = parser.parse(request.args.get('end'))

    if event_id:
        event = event_dao.get_event(event_id)
    elif recur_id:
        event = event_dao.generate_event(recur_id, start=start, end=end)
        recur_event = event_dao.get_group_event(recur_id=recur_id)
    else:
        event = Event(id="", title="", start=start, end=end, all_day=request.args.get('allDay'))
    return render_template('event_modal.html', event=event, timezone=timezone, recur_event=recur_event,
                           form=FlaskForm())


@application.route('/render_recurrent', methods=['GET'])
@flask_login.login_required
def render_recurrent():
    recur_id = request.args.get('recurId')
    event_id = request.args.get('eventId')
    start = parser.parse(request.args.get('start'))
    end = parser.parse(request.args.get('end'))
    init_start = parser.parse(request.args.get('initStart'))
    timezone = pytz.timezone(request.args.get('timeZone'))
    all_day = request.args.get('allDay')
    title = request.args.get('eventTitle')
    description = request.args.get('description')
    return render_template('recurrent_modal.html', timezone=timezone,
                           event=Event(id=event_id, recur_id=recur_id, start=start, end=end, init_start=init_start,
                                       all_day=all_day, title=title, description=description),
                           form=FlaskForm())


@bp.record_once
def on_load(state):
    login_manager.init_app(state.app)
