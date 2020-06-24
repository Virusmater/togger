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
        group_id = request.args.get('groupId')
        event = event_dao.generate_event(group_id, start=request.args.get('startDateTime'),
                                         end=request.args.get('endDateTime'))
    return render_template('shifts_modal.html',
                           event=event, time_zone=time_zone, form=FlaskForm())


@application.route('/render_event', methods=['GET'])
@flask_login.login_required
def render_event(timezone=None):
    if request.args.get('timeZone'):
        timezone = pytz.timezone(request.args.get('timeZone'))
    event_id = request.args.get('id')
    group_id = request.args.get('groupId')

    if request.args.get('startDateTime'):
        start = parser.parse(request.args.get('startDateTime'))
    if request.args.get('endDateTime'):
        end = parser.parse(request.args.get('endDateTime'))

    if event_id:
        event = event_dao.get_event(event_id)
    elif group_id:
        event = event_dao.generate_event(group_id, start=start, end=end)
    else:
        event = Event(id="", title="", start=start, end=end, all_day=request.args.get('allDay'))
    return render_template('event_modal.html', event=event, timezone=timezone, form=FlaskForm())


@bp.record_once
def on_load(state):
    login_manager.init_app(state.app)
