from flask.ext.wtf import Form
from flask_wtf.file import FileAllowed, FileField, FileRequired, InputRequired
from wtforms.fields import FieldList, FormField, RadioField, SubmitField


class UploadForm(Form):
    csv = FileField('CSV File', validators=[
        FileAllowed(['csv'], 'Must be a CSV file'),
        FileRequired()
    ])
    submit = SubmitField('Upload')


class DetermineDescriptorTypeForm(Form):
    descriptor_type = RadioField('Descriptor Type', choices=[
        ('text', 'Text Descriptor'),
        ('option', 'Option Descriptor')
    ])


class NextCancelBackForm(Form):
    submit_next = SubmitField('Next')
    submit_cancel = SubmitField('Cancel')
    submit_back = SubmitField('Back')


class DetermineDescriptorTypesForm(Form):
    descriptor_types = FieldList(RadioField('Descriptor Type', choices=[
        ('text', 'Text'),
        ('option', 'Option')
    ], validators=[InputRequired()]))
    progress = FormField(NextCancelBackForm)
