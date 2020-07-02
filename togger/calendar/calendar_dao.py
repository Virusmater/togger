import flask_login
from flask import flash
from flask.json import dumps

from togger import db
from togger.auth import auth_dao
from togger.auth.models import Role
from togger.calendar.models import Share, Calendar


@auth_dao.has_role(Role.OWNER)
def save_settings(settings):
    calendar = get_current_calendar()
    calendar.settings = dumps(settings)
    db.session.merge(calendar)
    db.session.commit()
    return True


@auth_dao.has_role(Role.MANAGER)
def share_calendar(role_name):
    if int(role_name) <= auth_dao.get_role().type and role_name < Role.OWNER:
        return Share(role_type=role_name, calendar_id=get_current_calendar().id)


@auth_dao.has_role(Role.OWNER)
def get_shares():
    calendar = get_current_calendar()
    roles = Role.query.filter(Role.calendar_id == calendar.id).all()
    return roles


@auth_dao.has_role(Role.OWNER)
def change_share(user_id, role_type):
    calendar = get_current_calendar()
    role = Role.query.filter(Role.calendar_id == calendar.id).filter(Role.user_id == user_id).first()
    if role.type >= Role.OWNER:
        flash('Not possible to change the permission of the current owner.', 'warning')
        return role
    if role_type > 0:
        if role_type >= Role.OWNER:
            set_owner(user_id)
            flash("Ownership for the calendar was transferred.", 'success')
        else:
            role.type = role_type
            flash("Permission changed", 'success')
            db.session.merge(role)
    else:
        db.session.delete(role)
    db.session.commit()
    return role


def accept_share(share_token):
    share = Share(token=share_token)
    if share.is_valid():
        for role in flask_login.current_user.roles:
            role.is_default = False
            if role.calendar_id == share.calendar_id:
                if role.type < share.role_type:
                    db.session.delete(role)
                    db.session.flush()
                    break
                else:
                    return
        role = Role(type=share.role_type, calendar_id=share.calendar_id,
                    is_default=True)
        flask_login.current_user.roles.append(role)
        db.session.merge(flask_login.current_user)
        db.session.commit()
        flash("New calendar was added", 'success')


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


@auth_dao.has_role(Role.OWNER)
def set_owner(user_id):
    for role in get_shares():
        if str(role.user_id) == user_id:
            role.type = Role.OWNER
        else:
            if role.type == Role.OWNER:
                role.type = Role.MANAGER
        db.session.merge(role)
    db.session.commit


@auth_dao.has_role(Role.OWNER)
def delete():
    db.session.delete(get_current_calendar())
    db.session.commit()
