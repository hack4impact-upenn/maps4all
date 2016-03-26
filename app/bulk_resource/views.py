import csv
from flask import redirect, render_template, url_for
from flask.ext.login import login_required
from . import bulk_resource
from forms import UploadForm


@bulk_resource.route('/upload', methods=['GET', 'POST'])
@login_required
def index():
    """Upload new resources in bulk with CSV file."""
    form = UploadForm()
    if form.validate_on_submit():
        file = form.csv.data
        # Read CSV file line-by-line.
        # TODO: Save CSV data somewhere instead of just printing it.
        with file.stream as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                print ', '.join(row)
        return redirect(url_for('bulk_resource.review'))
    return render_template('bulk_resource/upload.html', form=form)


@bulk_resource.route('/review')
@login_required
def review():
    return render_template('bulk_resource/review.html')
