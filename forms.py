"""Journal forms."""

# from flask_wtf import Form
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import (DataRequired, Regexp, Email, ValidationError,
                                Length, EqualTo)
from models import User


def name_exists(form, field):
    """Check if the username already exists."""
    if User.select().where(User.username == field.data).exists():
        raise ValidationError('User with that name already exists.')


def email_exists(form, field):
    """Check if the email already exists."""
    if User.select().where(User.email == field.data).exists():
        raise ValidationError('User with that email already exists.')


class RegisterForm(FlaskForm):
    """User registration form."""

    username = StringField(
        'Username',  # Form label
        validators=[
            DataRequired(),
            Regexp(
                r'^[a-zA-Z0-9_]+$',
                message=("Username should be one word, letters, "
                         "numbers and underscores only")
            ),
            name_exists
        ])
    email = StringField(
        'Email',  # Form label
        validators=[
            DataRequired(),
            Email(),
            email_exists
        ])
    password = PasswordField(
        'Password',  # Form label
        validators=[
            DataRequired(),
            Length(min=2),
            EqualTo('password2', message='Passwords must match.')
        ])
    password2 = PasswordField(
        'Confirm Password',  # Form label
        validators=[DataRequired()]
    )


class LoginForm(FlaskForm):
    """User login form."""

    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
