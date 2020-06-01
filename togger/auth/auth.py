import flask_login
from flask import Blueprint, request, redirect, url_for, render_template, flash
from flask_login import LoginManager
from werkzeug.security import check_password_hash, generate_password_hash
from togger import db
from .models import User

bp = Blueprint("auth", __name__, url_prefix="/auth")
login_manager = LoginManager()


class FlaskUser(flask_login.UserMixin):
    pass


def get_users():
    return User.query.all()


def get_user(username):
    if username is None:
        return
    return next((item for item in get_users() if item.username == username), None)


def add_user(username, password):
    if username is None or password is None:
        return
    user = User(username=username, password=generate_password_hash(password))
    db.session.add(user)
    db.session.commit()


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        if flask_login.current_user.is_authenticated:
            return redirect(url_for('main'))
        else:
            return render_template('login.html')
    email = request.form['email']
    if get_user(email) and check_password_hash(get_user(email).password, request.form['password']):
        user = FlaskUser()
        user.id = email
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
        add_user(email, request.form['password'])
        user = FlaskUser()
        user.id = email
        flask_login.login_user(user)
        return redirect(url_for('main'))
    flash('Such user already exists')
    return redirect(url_for('auth.register'))


@login_manager.user_loader
def user_loader(email):
    if get_user(email) is None:
        return

    user = FlaskUser()
    user.id = email
    return user


@login_manager.request_loader
def request_loader(request):
    email = request.form.get('email')
    if get_user(email) is None:
        return

    user = FlaskUser()
    user.id = email
    user.is_authenticated = check_password_hash(get_user(email)['password'], request.form['password'])

    return user


@login_manager.unauthorized_handler
def unauthorized_handler():
    return redirect(url_for('auth.login'))


@bp.record_once
def on_load(state):
    login_manager.init_app(state.app)
