import csv
from flask import redirect, render_template, url_for
from flask.ext.login import login_required
from . import bulk_resource
from forms import UploadForm


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
            csv_reader = csv.reader(csv_file)
            all_rows = ""
            for row in csv_reader:
                all_rows += str(row)
            print all_rows
        return redirect(url_for('bulk_resource.review'))
    return render_template('bulk_resource/upload.html', form=form)


@bulk_resource.route('/review')
@login_required
def review():
    return render_template('bulk_resource/review.html')
