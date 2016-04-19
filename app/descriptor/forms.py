from flask.ext.wtf import Form
from wtforms.fields import (
    BooleanField,
    FieldList,
    SelectField,
    SubmitField,
    TextField
)
from wtforms.validators import InputRequired, Length


class NewDescriptorForm(Form):
    desc_type = SelectField('Descriptor type',
                            choices=[('Text', 'Text'), ('Option', 'Option')],
                            validators=[InputRequired()]
                            )
    name = TextField('Name', validators=[InputRequired(), Length(1, 64)])
    option_values = FieldList(TextField('Option', [Length(0, 64)]))
    is_searchable = BooleanField('Searchable')
    submit = SubmitField('Add descriptor')


class EditDescriptorNameForm(Form):
    name = TextField('Name', validators=[InputRequired(), Length(1, 64)])
    submit = SubmitField('Update name')


class EditDescriptorOptionValueForm(Form):
    value = TextField('Option Value',
                      validators=[InputRequired(), Length(1, 64)])
    submit = SubmitField('Update option value')


class FixAllResourceOptionValueForm(Form):
    submit = SubmitField('Update resource option values')
