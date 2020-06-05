# togger
Togger is an easy to use sign up sheet for volunteers. Also can be used for various events planing like football matches 
or going out with friends

Demo: https://togger-app.herokuapp.com . Can take few moments for a cold boot. 
Registration doesn't require an email verification. 
* Plan events. Resize and drag em how you want
* Sign up yourself or your friend for a shift
* Count number of shifts per person for a given period
* Different colors for events based on number of people signed up: gray - nobody yet, orange - one person, green - two or more
* Mobile friendly
* Powered by Flask, Fullcalendar and many more

# how to use
1. Click Edit button to activate Edit mode
2. Select date to create an event (you can select multiple days, resize and drag events)
3. Click Stop button to go back to View mode
4. Select an event to sign up for the event
5. Uncheck a person from the list to remove them from an event

# screenshots


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
    build: .
    ports:
      - "5001:80"
```
* Change SECRET_KEY to something more secure
* Put your database uri in SQLALCHEMY_DATABASE_URI (or use sqlite by default)

run

`$ docker-compose up`

Currently ARM isn't supported, but feel free to use your own base image.

The repository also contains Procfile and Dockerfile to run the app on heroku
