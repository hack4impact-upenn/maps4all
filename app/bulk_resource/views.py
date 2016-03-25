import csv
from datetime import datetime
from flask import redirect, render_template, url_for
from flask.ext.login import login_required
from . import bulk_resource
from .. import db
from forms import UploadForm
from ..models import CsvCell, CsvContainer, CsvRow


@bulk_resource.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    """Upload new resources in bulk with CSV file."""
    form = UploadForm()
    if form.validate_on_submit():
        csv_data = form.csv.data
        # Read CSV file line-by-line.
        # TODO: Save CSV data somewhere instead of just printing it.
        with csv_data.stream as csv_file:
            # Create new CSV container object to hold contents of CSV file.
            csv_container = CsvContainer(
                date_uploaded=datetime.now(),
                file_name=csv_data.filename,
            )
            # csv_container.user = current_user

            # Iterate through the CSV file row-by-row and then cell-by-cell.
            # Each cell contains one comma-separated string in a row of a CSV
            # file.
            csv_reader = csv.reader(csv_file)
            for row in csv_reader:
                csv_row = CsvRow(csv_container=csv_container)
                for cell_data in row:
                    csv_cell = CsvCell(data=cell_data, csv_row=csv_row)
                    db.session.add(csv_cell)
                db.session.add(csv_row)
            db.session.add(csv_container)
            db.session.commit()
        return redirect(url_for('bulk_resource.review'))
    return render_template('bulk_resource/upload.html', form=form)


@bulk_resource.route('/review')
@login_required
def review():
    return render_template('bulk_resource/review.html')
