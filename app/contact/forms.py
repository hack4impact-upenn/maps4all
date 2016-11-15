from flask.ext.wtf import Form
from wtforms.fields import (
    StringField,
    SelectField,
    TextField,
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
    message = TextAreaField('Message', validators=[
        InputRequired(),
        Length(1, 1024),
    ])
    submit = SubmitField('Submit')

class ContactCategoryForm(Form):
    name = StringField('Name', validators=[
        InputRequired(),
        Length(1, 128),
    ])
    submit = SubmitField('Add Category')

class EditCategoryNameForm(Form):
    name = TextField('Name', validators=[
        InputRequired(),
        Length(1, 128),
    ])
    submit = SubmitField('Update name')

