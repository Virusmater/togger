import flask_login
from flask import Blueprint, render_template, request, jsonify, url_for
from flask_login import login_manager, LoginManager
from werkzeug.utils import redirect

from togger import application
from togger.auth import auth_api
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











@application.route('/shares', methods=['GET'])
@flask_login.login_required
def render_shares():
    shares = calendar_dao.get_shares()
    return render_template('shares.html', calendar=calendar_dao.get_current_calendar(), shares=shares)


@bp.record_once
def on_load(state):
    login_manager.init_app(state.app)
