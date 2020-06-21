import smtplib
from email.message import EmailMessage
from functools import wraps
from threading import Thread

import flask_login
from flask import flash, current_app

from togger import db
from togger.auth.models import User, Role
from togger.calendar.models import Calendar


def get_user(username):
    if username is None:
        return
    user = User.query.filter(User.username == username).first()
    return user


def get_user_by_id(id):
    if id is None:
        return
    user = User.query.filter(User.alias_id == id).first()
    return user


def add_user(username, password, first_name, last_name):
    if username is None or password is None:
        return
    calendar = Calendar(name=username)
    role = Role(type=Role.OWNER, calendar=calendar, is_default=True)
    user = User(username=username, first_name=first_name, last_name=last_name, roles=[role])
    user.set_password(password)
    verify_email(user)
    db.session.add(user)
    db.session.commit()
    return user


def update_user(first_name, last_name):
    user = flask_login.current_user
    user.first_name = first_name
    user.last_name = last_name
    db.session.merge(user)
    db.session.commit()
    return True


def verify_email(user):
    token = user.generate_validate_token()
    url = current_app.config['APP_URL'] + "/auth/verify/" + token
    subject = "[Togger] Welcome to Togger. Verify your email"
    prepare_email(user.username, subject, url)


def restore_password(token, new_password):
    user = User()
    if user.check_password_token(token):
        user = get_user(user.username)
        user.set_password(new_password)
        db.session.merge(user)
        db.session.commit()
        flask_login.login_user(user, remember=True)
        return True
    else:
        flash("Restoration link got expired. Please request a new one.", 'danger')
        return False


def password_email(username):
    user = get_user(username)
    if user and user.is_verified:
        token = user.generate_password_token()
        url = current_app.config['APP_URL'] + "/auth/restore/" + token
        subject = "[Togger] Forgot your password? The restoration link is inside"
        prepare_email(user.username, subject, url)


def prepare_email(address, subject, content):
    thread = Thread(target=send_email,
                    args=(address, subject, content, current_app.config,))
    thread.daemon = True
    thread.start()


def send_email(username, subject, content, config):
    msg = EmailMessage()
    msg.set_content(content)
    msg['Subject'] = subject
    msg['From'] = config['SMTP_MAILBOX']
    msg['To'] = username
    s = smtplib.SMTP(config['SMTP_SERVER'], config['SMTP_PORT'])
    s.login(config['SMTP_LOGIN'], config['SMTP_PASSWORD'])
    s.send_message(msg)
    s.quit()


def confirm_verify_email(token):
    user = User()
    if user.check_validate_token(token):
        user = get_user(user.username)
        user.is_verified = True
        db.session.merge(user)
        db.session.commit()
    else:
        flash('Verification link got expired. Please request a new one.', 'danger')


def change_password(old_password, new_password):
    if flask_login.current_user.check_password(old_password):
        flask_login.current_user.set_password(new_password)
        db.session.merge(flask_login.current_user)
        db.session.commit()
        flash('Password was changed. Please sign in using new password.', 'success')
        return True
    flash('Current password is incorrect.', 'danger')
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


def has_role(role_type):
    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            role = get_role()
            if role and role.type >= role_type:
                result = function(*args, **kwargs)
            else:
                result = current_app.login_manager.unauthorized()
            return result

        return wrapper

    return decorator
