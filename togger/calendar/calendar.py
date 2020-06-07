import flask_login
from flask import Blueprint, render_template, request, jsonify, url_for
from flask_login import login_manager, LoginManager
from werkzeug.utils import redirect

from togger import application
from togger.calendar import calendar_api

bp = Blueprint("calendar", __name__)
login_manager = LoginManager()


@application.route('/settings')
@flask_login.login_required
def render_settings():
    return render_template('settings.html', settings=calendar_api.get_settings())


@application.route('/render_share', methods=['GET'])
@flask_login.login_required
def render_share():
    return render_template('share_modal.html')


@application.route('/post_share', methods=['POST'])
@flask_login.login_required
def post_share():
    role_name = request.form['roleName']
    share = calendar_api.share_calendar(role_name)
    if share:
        url = request.host_url + "?share=" + str(share.id)
    else:
        url = ""
    return url


@application.route('/post_settings', methods=['POST'])
@flask_login.login_required
def post_settings():
    settings = {'scrollTime': request.form['scrollTime'], 'firstDay': request.form['firstDay'],
                'slotMinTime': request.form['slotMinTime'], 'slotMaxTime': request.form['slotMaxTime'],
                'nextDayThreshold': request.form['nextDayThreshold']}
    calendar_api.save_settings(settings)
    return '', 204


@application.route('/get_settings', methods=['GET'])
@flask_login.login_required
def get_settings():
    return jsonify(calendar_api.get_settings())


@application.route('/set_default', methods=['POST'])
@flask_login.login_required
def set_default():
    calendar_api.set_default(request.form['calendarId'])
    return redirect(url_for('main'))


@bp.record_once
def on_load(state):
    login_manager.init_app(state.app)
