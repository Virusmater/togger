import flask_login
from flask import Blueprint, render_template, request, jsonify, url_for
from flask_login import login_manager, LoginManager
from werkzeug.utils import redirect

from togger import application
from togger.auth import auth_api
from togger.calendar import calendar_api

bp = Blueprint("calendar", __name__, template_folder="templates")
login_manager = LoginManager()


@application.route('/settings')
@flask_login.login_required
def render_settings():
    return render_template('settings.html', calendar=calendar_api.get_current_calendar())


@flask_login.login_required
def create_calendar():
    calendar_name = request.form['calendarName']
    calendar_api.create(calendar_name)
    return redirect(url_for('main'))


@application.route('/render_delete', methods=['GET'])
@flask_login.login_required
def render_delete():
    return render_template('delete_modal.html')


@application.route('/calendars', methods=['POST'])
@flask_login.login_required
def post_calendars():
    if '_method' not in request.form:
        return create_calendar()
    elif request.form['_method'] == "DELETE":
        return delete_calendar()


@application.route('/calendars', methods=['DELETE'])
@flask_login.login_required
def delete_calendar():
    calendar_api.delete()
    return redirect(url_for('main'))


@application.route('/render_share', methods=['GET'])
@flask_login.login_required
def render_share():
    return render_template('share_modal.html')


@application.route('/render_new', methods=['GET'])
@flask_login.login_required
def render_new():
    return render_template('new_modal.html')


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


@application.route('/change_share', methods=['POST'])
@flask_login.login_required
@auth_api.can_edit_events
def change_share():
    user_id = request.form['userId']
    role_name = request.form['roleName']
    calendar_api.change_share(user_id, role_name)
    return '', 204


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
    return redirect(request.referrer)


@application.route('/shares', methods=['GET'])
@flask_login.login_required
def render_shares():
    shares = calendar_api.get_shares()
    return render_template('shares.html', calendar=calendar_api.get_current_calendar(), shares=shares)


@bp.record_once
def on_load(state):
    login_manager.init_app(state.app)
