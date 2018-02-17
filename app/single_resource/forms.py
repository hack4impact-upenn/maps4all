from flask.ext.wtf import Form
from wtforms.fields import FloatField, HiddenField, StringField, SubmitField
from wtforms.validators import InputRequired, Length


class SingleResourceForm(Form):
    name = StringField('Name', validators=[
        InputRequired(),
        Length(1, 500)
    ])
    address = StringField('Address', validators=[
        InputRequired(),
        Length(1, 500)
    ])
    latitude = FloatField('Latitude')
    longitude = FloatField('Longitude')
    submit = SubmitField('Save Resource')
