from flask.ext.wtf import Form
<<<<<<< HEAD
from wtforms.fields import FloatField, StringField, SubmitField
from wtforms.validators import InputRequired, Length, Optional
=======
from wtforms.fields import FloatField, HiddenField, StringField, SubmitField
from wtforms.validators import InputRequired, Length
>>>>>>> master


class SingleResourceForm(Form):
    name = StringField('Name', validators=[
        InputRequired(),
        Length(1, 500)
    ])
    address = StringField('Address', validators=[
        InputRequired(),
        Length(1, 500)
    ])
<<<<<<< HEAD
    latitude = FloatField('Latitude', validators=[
        Optional()
    ])
    longitude = FloatField('Longitude', validators=[
        Optional()
    ])
=======
    latitude = FloatField('Latitude')
    longitude = FloatField('Longitude')
>>>>>>> master
    submit = SubmitField('Save Resource')

    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return False
        if not self.latitude.data or not self.longitude.data:
            self.address.errors.append('Please select a valid address')
            return False
        return True
