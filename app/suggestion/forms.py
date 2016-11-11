from flask.ext.wtf import Form
from wtforms.fields import SubmitField, TextField, StringField
from wtforms.validators import Email, InputRequired, Length


class SuggestionContactForm(Form):
    contact_name = TextField(
        'Contact Name',
        validators=[InputRequired(), Length(1, 512)]
    )
    contact_email = TextField(
        'Email',
        validators=[InputRequired(), Length(1, 512), Email()]
    )
    contact_phone_number = TextField(
        'Phone Number',
        validators=[InputRequired(), Length(1, 64)]
    )

class SuggestionBasicForm(Form):
    name = StringField('Name', validators=[
        InputRequired(),
        Length(1, 512)
    ])
    address = StringField('Address', validators=[
        InputRequired(),
        Length(1, 512)
    ])
    suggestion_text = TextField('Suggestion', validators=[
        InputRequired()
    ])
    submit = SubmitField('Submit')

class SuggestionAdvancedForm(Form):
    name = StringField('Name', validators=[
        InputRequired(),
        Length(1, 512)
    ])
    address = StringField('Address', validators=[
        InputRequired(),
        Length(1, 512)
    ])
    suggestion_text = TextField('Suggestion', validators=[
        InputRequired()
    ])
    submit = SubmitField('Submit')