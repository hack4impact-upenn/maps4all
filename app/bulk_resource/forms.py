from flask.ext.wtf import Form
from flask_wtf.file import FileAllowed, FileField, FileRequired
from wtforms.fields import BooleanField, SubmitField


class UploadForm(Form):
    csv = FileField('CSV File', validators=[
        FileAllowed(['csv'], 'Must be a CSV file'),
        FileRequired()
    ])
    submit = SubmitField('Upload')


class InferDescriptorForm(Form):
    # descriptor_types = FormField(form_class=CreateDescriptorForm)
    submit = SubmitField('Save')


class CreateDescriptorForm(Form):
    descriptor_type = BooleanField('Descriptor Type')
