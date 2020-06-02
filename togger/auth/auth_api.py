from werkzeug.security import generate_password_hash

from togger import db
from togger.auth.models import User
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


def add_user(username, password):
    if username is None or password is None:
        return
    calendar = Calendar(name="default")
    user = User(username=username,calendars=[calendar])
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return user
