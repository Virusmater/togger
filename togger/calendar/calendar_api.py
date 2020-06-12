from datetime import datetime

import flask_login
from flask.json import dumps, loads

from togger import db
from togger.auth.models import Role
from togger.auth import auth_api
from togger.calendar.models import Share, Calendar

ROLES = ["user", "manager"]


@auth_api.can_edit_events
def save_settings(settings):
    calendar = get_current_calendar()
    calendar.settings = dumps(settings)
    db.session.merge(calendar)
    db.session.commit()
    return True


@auth_api.can_edit_events
def share_calendar(role_name):
    if role_name in ROLES:
        share = Share(calendar=get_current_calendar(), role_name=role_name)
        db.session.add(share)
        db.session.commit()
        return share
    return None


@auth_api.can_edit_events
def get_shares():
    calendar = get_current_calendar()
    roles = Role.query.filter(Role.calendar_id == calendar.id).all()
    return roles


@auth_api.can_edit_events
def change_share(user_id, role_name):
    calendar = get_current_calendar()
    role = Role.query.filter(Role.calendar_id == calendar.id).filter(Role.user_id == user_id).first()
    if role_name in ROLES:
        role.type = role_name
        db.session.merge(role)
    else:
        db.session.delete(role)
    db.session.commit()
    return role


def accept_share(share_id):
    share = Share.query.filter(Share.id == share_id).first()
    user = flask_login.current_user
    for role in user.roles:
        if role.calendar_id == share.calendar_id:
            return
    if datetime.now() < share.valid_until:
        for role in user.roles:
            role.is_default = False
        role = Role(type=share.role_name, calendar_id=share.calendar_id, is_default=True)
        flask_login.current_user.roles.append(role)
        db.session.merge(flask_login.current_user)
        db.session.commit()


def get_current_calendar():
    for role in flask_login.current_user.roles:
        if role.is_default:
            return role.calendar
    else:
        return None
    return role.calendar


def set_default(calendar_id):
    for role in flask_login.current_user.roles:
        role.is_default = str(role.calendar_id) == calendar_id
        db.session.merge(role)
    db.session.commit()


def create(calendar_name):
    user = flask_login.current_user
    calendar = Calendar(name=calendar_name)
    for role in user.roles:
        role.is_default = False
    role = Role(type="manager", calendar=calendar, is_default=True)
    user.roles.append(role)
    db.session.merge(user)
    db.session.commit()
    return calendar


@auth_api.can_edit_events
def delete():
    db.session.delete(get_current_calendar())
    db.session.commit()
