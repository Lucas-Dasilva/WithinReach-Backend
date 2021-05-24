from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, TextAreaField, validators, ValidationError, PasswordField, BooleanField
from wtforms.validators import ValidationError, DataRequired, EqualTo, Length
from wtforms.ext.sqlalchemy.fields import QuerySelectMultipleField
from wtforms.widgets import ListWidget, CheckboxInput

from app.models import Post, User


class SortForm(FlaskForm):
    sort = SelectField('Choose sorting:', choices=[(2, 'New'), (1, 'Hot')])
    submit = SubmitField('Refresh')

class PostForm(FlaskForm):
    body = TextAreaField('Body', [validators.required(), validators.length(min = 1, max = 1500, message = "(0-1500 characters)")])
    submit = SubmitField('Post')

class ReplyForm(FlaskForm):
    body = TextAreaField('Body', [validators.required(), validators.length(min = 1, max = 1500, message = "(0-1500 characters)")])
    submit = SubmitField('Post')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Username taken! Choose a different username.')