from flask.ext.wtf import Form
from wtforms.fields import (
    BooleanField,
    PasswordField,
    SubmitField
)
from wtforms.fields.html5 import EmailField
from wtforms.validators import Email, InputRequired, Length


class LoginForm(Form):
    email = EmailField('Email', validators=[
        InputRequired(),
        Length(1, 64),
        Email()
    ])
    password = PasswordField('Password', validators=[InputRequired()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log in')
