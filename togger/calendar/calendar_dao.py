import flask_login
from flask.json import dumps

from togger import db
from togger.auth import auth_dao
from togger.auth.models import Role
from togger.calendar.models import Share, Calendar


@auth_dao.can_edit_events
def save_settings(settings):
    calendar = get_current_calendar()
    calendar.settings = dumps(settings)
    db.session.merge(calendar)
    db.session.commit()
    return True


@auth_dao.can_edit_events
def share_calendar(role_name):
    print(role_name)
    print(auth_dao.get_role().type)
    if int(role_name) <= auth_dao.get_role().type:
        return Share(role_name=role_name, calendar_id=get_current_calendar().id)


@auth_dao.can_edit_events
def get_shares():
    calendar = get_current_calendar()
    roles = Role.query.filter(Role.calendar_id == calendar.id).all()
    return roles


@auth_dao.can_edit_events
def change_share(user_id, role_name):
    # don't allow to change to the role with higher access
    if auth_dao.get_role().type < role_name:
        return
    calendar = get_current_calendar()
    role = Role.query.filter(Role.calendar_id == calendar.id).filter(Role.user_id == user_id).first()
    if role_name > 0:
        # if current role is owner - don't change it to something lower - everybody will loose the access
        if role.type >= 100:
            return role
        role.type = role_name
        db.session.merge(role)
    else:
        db.session.delete(role)
    db.session.commit()
    return role


def accept_share(share_token):
    share = Share(token=share_token)
    user = flask_login.current_user
    for role in user.roles:
        if role.calendar_id == share.calendar_id:
            return
    if share.is_valid():
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
    role = Role(type=Role.OWNER, calendar=calendar, is_default=True)
    user.roles.append(role)
    db.session.merge(user)
    db.session.commit()
    return calendar


@auth_dao.can_edit_events
def delete():
    db.session.delete(get_current_calendar())
    db.session.commit()
