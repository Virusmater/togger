import flask_login
from flask import Blueprint, render_template, request
from flask_login import login_manager, LoginManager

from togger import application
from togger.auth import auth_dao
from togger.auth.models import Role
from togger.calendar import calendar_dao

bp = Blueprint("calendar", __name__, template_folder="templates")
login_manager = LoginManager()


@application.route('/settings')
@flask_login.login_required
def render_settings():
    return render_template('settings.html', calendar=calendar_dao.get_current_calendar())


@application.route('/render_delete', methods=['GET'])
@flask_login.login_required
def render_delete():
    return render_template('delete_modal.html')


@application.route('/render_share', methods=['GET'])
@flask_login.login_required
def render_share():
    return render_template('share_modal.html')


@application.route('/render_new', methods=['GET'])
@flask_login.login_required
def render_new():
    return render_template('new_modal.html')


@application.route('/render_transfer_ownership', methods=['GET'])
@flask_login.login_required
def render_transfer_ownership():
    form_id = request.args.get('form_id')
    return render_template('transfer_ownership.html', form_id=form_id)


@application.route('/shares', methods=['GET'])
@flask_login.login_required
@auth_dao.has_role(Role.OWNER)
def render_shares():
    shares = calendar_dao.get_shares()
    return render_template('shares.html', calendar=calendar_dao.get_current_calendar(), shares=shares)


@bp.record_once
def on_load(state):
    login_manager.init_app(state.app)
