from datetime import datetime

import flask_login
from flask.json import dumps, loads

from togger import db
from togger.auth.models import Role
from togger.auth import auth_api
from togger.calendar.models import Share

ROLES = ["user", "manager"]


@auth_api.can_edit_events
def save_settings(settings):
    calendar = get_current_calendar()
    calendar.settings = dumps(settings)
    db.session.merge(calendar)
    db.session.commit()
    return True


def get_settings():
    return loads(get_current_calendar().settings)


@auth_api.can_edit_events
def share_calendar(role_name):
    if role_name in ROLES:
        share = Share(calendar=get_current_calendar(), role_name=role_name)
        db.session.add(share)
        db.session.commit()
        return share
    return None


def accept_share(share_id):
    share = Share.query.filter(Share.id == share_id).first()
    if datetime.now() < share.valid_until:
        role = Role(type="manager", calendar_id=share.calendar_id, is_default=True)
        flask_login.current_user.roles.append(role)
        db.session.merge(flask_login.current_user)
        db.session.commit()


def get_current_calendar():
    for role in flask_login.current_user.roles:
        if role.is_default:
            return role.calendar
    return role.calendar


def set_default(calendar_id):
    for role in flask_login.current_user.roles:
        role.is_default = str(role.calendar_id) == calendar_id
        db.session.merge(role)
    db.session.commit()
