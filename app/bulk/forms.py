from flask.ext.wtf import Form
from flask_wtf.file import FileAllowed, FileField, FileRequired
from wtforms.fields import (
    SubmitField
)


class UploadForm(Form):
    csv = FileField('CSV File', validators=[
        FileRequired(),
        FileAllowed(['csv'], 'Must be a CSV file')
    ])
    submit = SubmitField('Upload')
