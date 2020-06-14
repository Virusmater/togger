from datetime import datetime, timedelta
from distutils.util import strtobool

import flask_login
from dateutil import parser
from dateutil.tz import UTC
from flask import Blueprint, render_template, request, jsonify
from flask_login import login_manager, LoginManager
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
def render_shifts():
    event_id = request.args.get('id')
    is_editable = bool(strtobool(request.args.get('isEditable')))
    event = event_dao.get_event(event_id)
    return render_template('shifts_modal.html', is_editable=is_editable,
                           event=event)


@application.route('/render_event', methods=['GET'])
@flask_login.login_required
def render_event():
    if request.args.get('id'):
        event = event_dao.get_event(request.args.get('id'))
    else:
        event = Event(id="", title="", start=request.args.get('startDateTime'), end=request.args.get('endDateTime'),
                      all_day=request.args.get('allDay'))
    return render_template('event_modal.html', event=event)





@bp.record_once
def on_load(state):
    login_manager.init_app(state.app)
