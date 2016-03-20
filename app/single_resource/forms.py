from flask.ext.wtf import Form
from wtforms.fields import FloatField, StringField, SubmitField
from wtforms.validators import InputRequired, Length


class CreateResourceForm(Form):
    name = StringField('Name', validators=[InputRequired(), Length(1, 64)])
    address = StringField('Address', validators=[
        InputRequired(),
        Length(1, 128)
    ])
    latitude = FloatField('Latitude', validators=[InputRequired()])
    longitude = FloatField('Longitude', validators=[InputRequired()])
    submit = SubmitField('Add')
