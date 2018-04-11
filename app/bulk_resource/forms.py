from flask.ext.wtf import Form
from flask_wtf.file import (
    InputRequired
)
from wtforms.fields import (
    FieldList,
    FormField,
    RadioField,
    SubmitField,
    TextAreaField,
    StringField,
    SelectField,
    SelectMultipleField
)


class NavigationForm(Form):
    submit_next = SubmitField('Next')
    submit_cancel = SubmitField('Cancel')
    submit_back = SubmitField('Back')

class DetermineRequiredOptionDescriptorForm(Form):
    required_option_descriptor = SelectField('Required Option Descriptor', validators=[InputRequired()])
    navigation = FormField(NavigationForm)

class DetermineDescriptorTypesForm(Form):
    descriptor_types = FieldList(RadioField(choices=[
        ('text', 'Text'),
        ('option', 'Option'),
        ('hyperlink', 'Hyperlink'),
    ], validators=[InputRequired()]))
    navigation = FormField(NavigationForm)

class RequiredOptionDescriptorMissingForm(Form):
    resources = FieldList(SelectMultipleField(validators=[InputRequired()]))
    navigation = FormField(NavigationForm)

class DetermineOptionsForm(Form):
    navigation = FormField(NavigationForm)

class SaveCsvDataForm(Form):
    submit = SubmitField('Save')
    submit_cancel = SubmitField('Cancel')
    submit_back = SubmitField('Back')
