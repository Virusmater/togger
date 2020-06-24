from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField
from wtforms.validators import DataRequired


class DeleteForm(FlaskForm):
    submit = SubmitField('Delete')


class NewForm(FlaskForm):
    calendarName = StringField('Calendar name', validators=[DataRequired()])
    submit = SubmitField('Create')


class SettingsForm(FlaskForm):
    scrollTime = StringField('Scroll Time', validators=[DataRequired()],
                             render_kw={"class": "form-control", 'placeholder': "16:00:00"})
    firstDay = StringField('First Day', validators=[DataRequired()],
                           render_kw={"class": "form-control", 'placeholder': "1"})
    slotMinTime = StringField('Slot Min Time', validators=[DataRequired()],
                              render_kw={"class": "form-control", 'placeholder': "09:00:00"})
    slotMaxTime = StringField('Slot Max Time', validators=[DataRequired()],
                              render_kw={"class": "form-control", 'placeholder': "21:00:00"})
    nextDayThreshold = StringField('Next Day Threshold', validators=[DataRequired()],
                                   render_kw={"class": "form-control", 'placeholder': "09:00:00"})
    submit = SubmitField('Save', render_kw={"class": "btn btn-primary"})
