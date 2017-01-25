from flask.ext.wtf import Form
from wtforms.fields import (
    BooleanField,
    FieldList,
    SelectField,
    SelectMultipleField,
    SubmitField,
    TextField
)
from wtforms.validators import InputRequired, Length


class NewDescriptorForm(Form):
    desc_type = SelectField('Descriptor type',
                            choices=[('Text', 'Text'), ('Option', 'Option')],
                            validators=[InputRequired()]
                            )
    name = TextField('Name', validators=[InputRequired(), Length(1, 500)])
    option_values = FieldList(TextField('Option', [Length(0, 500)]))
    is_searchable = BooleanField('Searchable')
    submit = SubmitField('Add descriptor')


class EditDescriptorNameForm(Form):
    name = TextField('Name', validators=[InputRequired(), Length(1, 500)])
    submit = SubmitField('Update name')


class EditDescriptorSearchableForm(Form):
    is_searchable = BooleanField('Searchable')
    submit = SubmitField('Update')


class EditDescriptorOptionValueForm(Form):
    value = TextField('Option Value',
                      validators=[InputRequired(), Length(1, 500)])
    submit = SubmitField('Update option value')


class AddDescriptorOptionValueForm(Form):
    value = TextField('', validators=[InputRequired(), Length(1, 500)])
    submit = SubmitField('Add option')


class FixAllResourceOptionValueForm(Form):
    submit = SubmitField('I understand, delete this option')


class ChangeRequiredOptionDescriptorForm(Form):
    submit = SubmitField('Change')


class RequiredOptionDescriptorMissingForm(Form):
    resources = FieldList(SelectMultipleField(validators=[InputRequired()]))
    submit = SubmitField('Update')
