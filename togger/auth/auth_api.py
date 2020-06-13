from functools import wraps

import flask_login
from flask import flash
from togger import db
from togger.auth.models import User, Role
from togger.calendar.models import Calendar


def get_users():
    return User.query.all()


# TODO: fix me in case of big users table
def get_user(username):
    if username is None:
        return
    return next((item for item in get_users() if item.username == username), None)


# TODO: fix me in case of big users table
def get_user_by_id(id):
    if id is None:
        return
    return next((item for item in get_users() if str(item.id) == id), None)


def add_user(username, password, first_name, last_name):
    if username is None or password is None:
        return
    calendar = Calendar(name=username)
    role = Role(type="manager", calendar=calendar, is_default=True)
    user = User(username=username, first_name=first_name, last_name=last_name, roles=[role])
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return user


def update_user(first_name, last_name):
    user = flask_login.current_user
    user.first_name = first_name
    user.last_name = last_name
    db.session.merge(user)
    db.session.commit()
    return user


def change_password(old_password, new_password):
    if flask_login.current_user.check_password(old_password):
        flask_login.current_user.set_password(new_password)
        db.session.merge(flask_login.current_user)
        db.session.commit()
        return True
    flash('Current password is incorrect')
    return False


def get_roles():
    try:
        return flask_login.current_user.roles
    except AttributeError:
        return []


def get_role():
    for role in get_roles():
        if role.is_default:
            return role
    return None


def can_edit_events(func):
    @wraps(func)
    def func_wrapper(*args, **kwargs):
        role = get_role()
        if role and role.can_edit_events:
            return func(*args, **kwargs)
        else:
            return '', 401
    return func_wrapper

