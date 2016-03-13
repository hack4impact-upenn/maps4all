from flask import redirect, render_template, url_for
from flask.ext.login import (
    login_required
)
from . import bulk
from forms import (
    UploadForm
)
import csv


@bulk.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    """Upload new resources in bulk with CSV file."""
    form = UploadForm()
    if form.validate_on_submit():
        file = form.csv.data
        # Read CSV file line-by-line.
        # Stand-in for future CSV parsing.
        with file.stream as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                print ', '.join(row)
        return redirect(url_for('bulk.review'))
    return render_template('bulk/upload.html', form=form)


@bulk.route('/review')
@login_required
def review():
    return render_template('bulk/review.html')
