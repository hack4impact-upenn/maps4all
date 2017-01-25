from flask.ext.wtf import Form
from wtforms.fields import SubmitField, TextField, StringField
from wtforms.validators import Email, InputRequired, Length


class SuggestionBasicForm(Form):
    contact_name = TextField(
        'Contact Name',
        validators=[InputRequired(), Length(1, 500)]
    )
    contact_email = TextField(
        'Email',
        validators=[InputRequired(), Length(1, 500), Email()]
    )
    contact_phone_number = TextField(
        'Phone Number',
        validators=[InputRequired(), Length(1, 64)]
    )
    name = StringField('Resource Name', validators=[
        InputRequired(),
        Length(1, 500)
    ])
    address = StringField('Resource Address', validators=[
        InputRequired(),
        Length(1, 500)
    ])
    suggestion_text = TextField('Suggestion', validators=[
        InputRequired()
    ])
    submit = SubmitField('Submit')

class SuggestionAdvancedForm(Form):
    """ CURRENTLY NOT IN USE
    Intention is to use this as an advanced suggestion form allowing users to
    also fill out descriptor values
    """
    contact_name = TextField(
        'Contact Name',
        validators=[InputRequired(), Length(1, 500)]
    )
    contact_email = TextField(
        'Email',
        validators=[InputRequired(), Length(1, 500), Email()]
    )
    contact_phone_number = TextField(
        'Phone Number',
        validators=[InputRequired(), Length(1, 64)]
    )
    name = StringField('Resource Name', validators=[
        InputRequired(),
        Length(1, 500)
    ])
    address = StringField('Resource Address', validators=[
        InputRequired(),
        Length(1, 500)
    ])
    suggestion_text = TextField('Suggestion', validators=[
        InputRequired()
    ])
    submit = SubmitField('Submit')