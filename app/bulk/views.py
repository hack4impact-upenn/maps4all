from flask import flash, redirect, render_template, url_for
from flask.ext.login import (
    login_required
)
from . import bulk
from forms import (
    UploadForm
)


@bulk.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    """Upload new resources in bulk with CSV file."""
    form = UploadForm()
    if form.validate_on_submit():
        csv = form.csv.data
        print csv
        flash('File successfully uploaded', 'form-success')
        return redirect(url_for('bulk.review'))
    return render_template('bulk/upload.html', form=form)


@bulk.route('/review')
@login_required
def review():
    return render_template('bulk/review.html')
