import flask_login
from flask import Blueprint, request
from flask_login import login_required

from togger.auth import auth_dao

bp = Blueprint("auth_api", __name__, url_prefix="/api/v1/users")


@bp.route("/", methods=['PUT', 'POST'])
@login_required
def update_user():
    auth_dao.update_user(first_name=request.form['firstName'], last_name=request.form['lastName'])
    return '', 204


@bp.route("/resend_email", methods=['POST'])
@login_required
def resend_email():
    user = flask_login.current_user
    auth_dao.verify_email(user)
    return '', 204
