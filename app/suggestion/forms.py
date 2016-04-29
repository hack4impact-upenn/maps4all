from flask.ext.wtf import Form
from wtforms.fields import SubmitField, TextField
from wtforms.validators import Email, InputRequired, Length


class SuggestionForm(Form):
    suggestion_text = TextField(
        'Suggestion',
        validators=[InputRequired()]
    )
    contact_name = TextField(
        'Contact Name',
        validators=[InputRequired(), Length(1, 64)]
    )
    contact_email = TextField(
        'Email',
        validators=[InputRequired(), Length(1, 64), Email()]
    )
    contact_phone_number = TextField(
        'Phone Number',
        validators=[InputRequired(), Length(1, 64)]
    )
    submit = SubmitField('Submit')
