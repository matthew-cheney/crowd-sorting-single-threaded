from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length, Email, ValidationError
from crowdsorting.database.models import *


class NewDocForm(FlaskForm):
    content = StringField('Content',
                          validators=[DataRequired(),
                                      Length(max=500)])
    submit = SubmitField('Submit Text')


class NewUserForm(FlaskForm):
    firstName = StringField('FirstName',
                            validators=[DataRequired(),
                                        Length(max=100)])
    lastName = StringField('LastName',
                           validators=[DataRequired(),
                                       Length(max=100)])
    email = StringField('Email',
                        validators=[DataRequired(),
                                    Length(max=120),
                                    Email()])

    submit = SubmitField('Sign Up')

    def validate_email(self, email):
        judge = Judge.query.filter_by(email=email.data).first()
        if judge:
            raise ValidationError('A user with that email already exists.')

    def validate_username(self, username):
        judge = Judge.query.filter_by(username=username.data).first()
        if judge:
            raise ValidationError(
                'That username is taken. Please choose a different one.')


class NewProjectForm(FlaskForm):
    projectName = StringField('ProjectName',
                              validators=[DataRequired(),
                                          Length(max=120)])
    submit = SubmitField('Create Project')
