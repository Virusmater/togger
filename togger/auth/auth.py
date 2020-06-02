import flask_login
from flask import Blueprint, request, redirect, url_for, render_template, flash, session
from flask_login import LoginManager, login_required, logout_user
from .auth_api import get_user, add_user, get_user_by_id

bp = Blueprint("auth", __name__, url_prefix="/auth")
login_manager = LoginManager()


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        if flask_login.current_user.is_authenticated:
            return redirect(url_for('main'))
        else:
            return render_template('login.html')
    email = request.form['email']
    user = get_user(email)
    if user and user.check_password(request.form['password']):
        flask_login.login_user(user)
        return redirect(url_for('main'))
    flash('Incorrect login or/and password. Please check it and try again')
    return redirect(url_for('auth.login'))


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        if flask_login.current_user.is_authenticated:
            return redirect(url_for('main'))
        else:
            return render_template('register.html')
    email = request.form['email']
    if get_user(email) is None:
        user = add_user(email, request.form['password'])
        flask_login.login_user(user)
        return redirect(url_for('main'))
    flash('Such user already exists')
    return redirect(url_for('auth.register'))


@bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@login_manager.user_loader
def user_loader(id):
    return get_user_by_id(id)


@login_manager.unauthorized_handler
def unauthorized_handler():
    return redirect(url_for('auth.login'))


@bp.record_once
def on_load(state):
    login_manager.init_app(state.app)
