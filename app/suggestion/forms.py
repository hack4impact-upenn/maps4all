from flask.ext.wtf import Form
from wtforms.fields import SubmitField, TextField, StringField
from wtforms.validators import Email, InputRequired, Length


class SuggestionBasicForm(Form):
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
    name = StringField('Resource Name', validators=[
        InputRequired(),
        Length(1, 512)
    ])
    address = StringField('Resource Address', validators=[
        InputRequired(),
        Length(1, 512)
    ])
    suggestion_text = TextField('Suggestion', validators=[
        InputRequired()
    ])
    submit = SubmitField('Submit')

class SuggestionAdvancedForm(Form):
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
    name = StringField('Resource Name', validators=[
        InputRequired(),
        Length(1, 512)
    ])
    address = StringField('Resource Address', validators=[
        InputRequired(),
        Length(1, 512)
    ])
    suggestion_text = TextField('Suggestion', validators=[
        InputRequired()
    ])
    submit = SubmitField('Submit')