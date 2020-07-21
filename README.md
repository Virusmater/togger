# togger
Togger is an easy to use sign up sheet for volunteers. Also can be used for various events planing like football matches 
or going out with friends

# demo
URL: https://togger-app.herokuapp.com (can take few moments for a cold boot)  
user: demo@github.com  
pass: demo

Registration doesn't require an email verification (but it will still annoy you because this is an only way to recover lost password). 
# features
* Plan events. Even recurrent ones. Resize and drag em how you want
* Sign up yourself or your friend for a shift
* Share calendar with your collective/family/friends
* Count number of shifts per person for a given period
* Control an access
* Different colors for events based on number of people signed up: gray - nobody yet, orange - one person, green - two or more
* Mobile friendly
* Powered by Python, Flask, Flask-Login, Fullcalendar, rrule, WTForms, SQLAlchemy and many more

# how to use
## create an event
1. Click the *Edit* button to activate an edit mode
2. Select the date to create an event (you can select multiple days, resize and drag events)
3. Put in the event title, description and recurrent preference
4. Click the *Save changes* button
5. Click the *Stop* button to go back to the View mode
## sign up for an event
1. Select an event
2. Press the *I'm in* button or manually put a name into the field
3. Click the *Save changes* button

# screenshots
![week view](/screenshots/week_view.png?raw=true "Week View")
![event view](/screenshots/event_view.png?raw=true "Event View")
![create view](/screenshots/create_view.png?raw=true "Create View")
![report_view](/screenshots/report_view.png?raw=true "Report View")

# docker-compose
```
version: '3'
services:
  togger:
    restart: always
    environment:
      - SECRET_KEY=change-me
      - SQLALCHEMY_DATABASE_URI=sqlite:///resources/database.db
      - MODULE_NAME=togger.main
      - VARIABLE_NAME=application
      - APP_URL=localhost
      - SMTP_LOGIN=
      - SMTP_MAILBOX=
      - SMTP_PASSWORD=
      - SMTP_PORT=
      - SMTP_SERVER=
    build: .
    ports:
      - "5001:80"
```
* Change SECRET_KEY to something more secure
* Put your database uri in SQLALCHEMY_DATABASE_URI or use sqlite by default (was tested with sqlite and postgresql only)
* Change APP_URL to you real app url (used in emails)
* Put SMTP parameters for an email validation and a password recovery

run

`$ docker-compose up`

Currently ARM isn't supported, but feel free to use your own base image.

The repository also contains Procfile to run the app on heroku

# TODO
* add LDAP auth
* ????
