from flask.ext.wtf import Form
from wtforms.fields import FloatField, StringField, SubmitField
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
    latitude = FloatField('Latitude', validators=[
        InputRequired()
    ])
    longitude = FloatField('Longitude', validators=[
        InputRequired()
    ])
    submit = SubmitField('Save Resource')
