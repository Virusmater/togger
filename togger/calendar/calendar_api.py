import flask_login
from flask import Blueprint, request, url_for, flash
from flask_wtf import FlaskForm
from werkzeug.utils import redirect

from togger.auth import auth_dao
from togger.auth.models import Role
from togger.calendar import calendar_dao
from togger.calendar.calendar_forms import DeleteForm, NewForm, SettingsForm

bp = Blueprint("calendar_api", __name__, url_prefix="/api/v1/calendars")


@bp.route('/', methods=['POST'])
@flask_login.login_required
def post_calendars():
    if '_method' not in request.form:
        if NewForm().validate_on_submit():
            calendar_dao.create(request.form['calendarName'])
        return redirect(url_for('main'))
    elif request.form['_method'] == "DELETE":
        return delete_calendar()


@bp.route('/', methods=['DELETE'])
@flask_login.login_required
@auth_dao.has_role(Role.OWNER)
def delete_calendar():
    if DeleteForm().validate_on_submit():
        calendar_dao.delete()
    return redirect(url_for('main'))


@bp.route('/share', methods=['POST'])
@flask_login.login_required
@auth_dao.has_role(Role.MANAGER)
def post_share():
    role_name = int(request.form['roleName'])
    share = calendar_dao.share_calendar(role_name)
    if share:
        url = request.host_url + "?share=" + share.generate_token()
    else:
        url = ""
    return url


@bp.route('/share', methods=['PUT'])
@flask_login.login_required
@auth_dao.has_role(Role.OWNER)
def change_share():
    if FlaskForm().validate_on_submit():
        user_id = request.form['userId']
        role_name = request.form['roleNameShares']
        calendar_dao.change_share(user_id, int(role_name))
    return '', 204


@bp.route('/settings', methods=['POST'])
@flask_login.login_required
def post_settings():
    if SettingsForm().validate_on_submit():
        settings = {'scrollTime': request.form['scrollTime'], 'firstDay': request.form['firstDay'],
                    'slotMinTime': request.form['slotMinTime'], 'slotMaxTime': request.form['slotMaxTime'],
                    'nextDayThreshold': request.form['nextDayThreshold']}
        if calendar_dao.save_settings(settings):
            flash("Settings saved", 'success')
    return redirect(url_for('render_settings'))


@bp.route('/default', methods=['POST'])
@flask_login.login_required
def set_default():
    calendar_dao.set_default(request.form['calendarId'])
    return redirect(request.referrer)
