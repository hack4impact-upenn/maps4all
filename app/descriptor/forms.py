from flask.ext.wtf import Form
from wtforms.fields import FieldList, SelectField, SubmitField, TextField
from wtforms.validators import InputRequired, Length


class NewDescriptorForm(Form):
    desc_type = SelectField('Descriptor type',
                            choices=[('Text', 'Text'), ('Option', 'Option')],
                            validators=[InputRequired()]
                            )
    name = TextField('Name', validators=[InputRequired(), Length(1, 64)])
    option_values = FieldList(TextField('Option', [Length(0, 64)]))
    submit = SubmitField('Add descriptor')


class ChangeNameForm(Form):
    name = TextField('Name', validators=[InputRequired(), Length(1, 64)])
    submit = SubmitField('Update name')


class EditResourceOptionForm(Form):
    value = TextField('Option Value',
                      validators=[InputRequired(), Length(1, 64)])
    submit = SubmitField('Update option value')
