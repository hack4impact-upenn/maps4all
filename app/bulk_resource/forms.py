from flask.ext.wtf import Form
from flask_wtf.file import (
    FileAllowed,
    FileField,
    FileRequired,
    InputRequired
)
from wtforms.fields import (
    FieldList,
    FormField,
    RadioField,
    SubmitField,
    TextAreaField
)


class UploadForm(Form):
    csv = FileField('CSV File', validators=[
        FileAllowed(['csv'], 'Must be a CSV file'),
        FileRequired()
    ])
    submit = SubmitField('Upload')


class NavigationForm(Form):
    submit_next = SubmitField('Next')
    submit_cancel = SubmitField('Cancel')
    submit_back = SubmitField('Back')


class DetermineDescriptorTypesForm(Form):
    descriptor_types = FieldList(RadioField(choices=[
        ('text', 'Text'),
        ('option', 'Option')
    ], validators=[InputRequired()]))
    navigation = FormField(NavigationForm)


class DetermineOptionsForm(Form):
    options = FieldList(TextAreaField())
    navigation = FormField(NavigationForm)
