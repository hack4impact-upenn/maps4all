from flask.ext.wtf import Form
from wtforms.fields import FloatField, StringField, SubmitField
from wtforms.validators import InputRequired, Length


class BaseForm(Form):
    pass


class SingleResourceForm(Form):
    name = StringField('Name', validators=[
        InputRequired(),
        Length(1, 512)
    ])
    address = StringField('Address', validators=[
        InputRequired(),
        Length(1, 512)
    ])
    latitude = FloatField('Latitude', validators=[
        InputRequired()
    ])
    longitude = FloatField('Longitude', validators=[
        InputRequired()
    ])
    submit = SubmitField('Save Resource')
