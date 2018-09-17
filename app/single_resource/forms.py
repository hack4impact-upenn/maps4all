from flask_wtf import Form
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
    latitude = FloatField('Latitude')
    longitude = FloatField('Longitude')
    submit = SubmitField('Save Resource')

    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return False
        if not self.latitude.data or not self.longitude.data:
            self.address.errors.append('Please select a valid address')
            return False
        return True
