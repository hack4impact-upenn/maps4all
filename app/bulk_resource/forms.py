import csv
from datetime import datetime

from flask.ext.login import current_user
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

from .. import db
from ..models import (
    CsvBodyCell,
    CsvBodyRow,
    CsvContainer,
    CsvHeaderCell,
    CsvHeaderRow,
)


class UploadForm(Form):
    csv = FileField('CSV File', validators=[
        FileAllowed(['csv'], 'Must be a CSV file'),
        FileRequired()
    ])
    submit = SubmitField('Upload')

    def validate_csv(self, field):
        """
        Validation for CSV files.
        """
        csv_data = field.data
        with csv_data.stream as csv_file:
            # Create new CSV container object to hold contents of CSV file.
            csv_container = CsvContainer(
                date_uploaded=datetime.now(),
                file_name=csv_data.filename,
                user=current_user
            )
            csv_reader = csv.reader(csv_file)

            # The first row of the CSV file contains the names of the columns.
            header_row = csv_reader.next()
            csv_header_row = CsvHeaderRow(
                csv_header_row_container=csv_container
            )
            required_columns = {
                'Name': False,
                'Address': False
            }
            for column_name in header_row:
                csv_cell = CsvHeaderCell(data=column_name,
                                         csv_header_row=csv_header_row)
                # Keep track of which required columns we have seen so far.
                if column_name in required_columns:
                    required_columns[column_name] = True
                db.session.add(csv_cell)
            db.session.add(csv_header_row)

            # Iterate through the CSV file row-by-row and then cell-by-cell.
            # Each cell contains one comma-separated string in a row of a CSV
            # file.
            for row in csv_reader:
                csv_body_row = CsvBodyRow(csv_container=csv_container)
                for cell_data in row:
                    csv_cell = CsvBodyCell(data=cell_data,
                                           csv_body_row=csv_body_row)
                    db.session.add(csv_cell)
                db.session.add(csv_body_row)
            db.session.add(csv_container)


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
