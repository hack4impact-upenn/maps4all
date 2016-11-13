from flask.ext.wtf import Form
from wtforms.fields import (
    StringField,
    SelectField,
    TextAreaField,
    SubmitField,
)
from wtforms.fields.html5 import EmailField
from wtforms.validators import (
    InputRequired,
    Email,
    Length,
)

class ContactForm(Form):
    name = StringField('Name', validators=[
        InputRequired(),
        Length(1, 128),
    ])
    email = EmailField('Email', validators=[
        InputRequired(),
        Length(1, 64),
        Email(),
    ])
    category = SelectField('Category', choices=[('Subject1', 'Subject1'), ('Subject2', 'Subject2')])
    message = TextAreaField('Message', validators=[
        InputRequired(),
        Length(1, 1024),
    ])
    submit = SubmitField('Submit')
