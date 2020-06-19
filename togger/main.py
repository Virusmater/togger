import flask_login
from flask import request, render_template, redirect, url_for

from togger import application
from togger.auth import auth_dao, auth_api
from togger.calendar import calendar_dao, calendar, calendar_api
from togger.event import event, event_api, event_dao
from .auth import auth

application.register_blueprint(event.bp)
application.register_blueprint(event_api.bp)
application.register_blueprint(calendar.bp)
application.register_blueprint(calendar_api.bp)
application.register_blueprint(auth_api.bp)
application.register_blueprint(auth.bp)


@application.route('/')
@flask_login.login_required
def main():
    if request.args.get('share'):
        calendar_dao.accept_share(request.args.get('share'))
        return redirect(url_for('main'))
    return render_template('main.html',
                           calendar=calendar_dao.get_current_calendar(), current_user=flask_login.current_user)


@application.route('/render_password', methods=['GET'])
@flask_login.login_required
def render_password():
    return render_template('password_modal.html')


@application.route('/change_password', methods=['POST'])
@flask_login.login_required
def change_password():
    old_password = request.form['oldPassword']
    new_password = request.form['newPassword']
    if auth_dao.change_password(old_password, new_password):
        return '', 204

    else:
        return render_password(), 500


@application.context_processor
def utility_processor():
    return dict(roles=auth_dao.get_roles, current_role=auth_dao.get_role, get_weekday=event_dao.get_weekday,
                get_weekday_occurrence=event_dao.get_weekday_occurrence, get_date=event_dao.get_date)
