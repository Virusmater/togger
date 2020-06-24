import flask_login
from flask import Blueprint, request, flash, url_for
from flask_login import login_required
from werkzeug.utils import redirect

from togger.auth import auth_dao
from togger.auth.auth import render_password

bp = Blueprint("auth_api", __name__, url_prefix="/api/v1/users")


@bp.route("/", methods=['PUT', 'POST'])
@login_required
def update_user():
    if auth_dao.update_user(first_name=request.form['firstName'], last_name=request.form['lastName']):
        flash("Profile updated", 'success')
    return redirect(url_for('auth.render_profile'))


@bp.route("/resend_email", methods=['POST'])
@login_required
def resend_email():
    user = flask_login.current_user
    auth_dao.verify_email(user)
    return '', 204


@bp.route('/password', methods=['POST'])
@flask_login.login_required
def change_password():
    old_password = request.form['oldPassword']
    new_password = request.form['newPassword']
    if auth_dao.change_password(old_password, new_password):
        return '', 204
    else:
        return render_password(), 500
