import csv
from datetime import datetime

from flask import abort, redirect, render_template, request, url_for
from flask.ext.login import current_user, login_required

from . import bulk_resource
from .. import db
from ..models import (
    CsvBodyCell,
    CsvBodyRow,
    CsvContainer,
    CsvHeaderCell,
    CsvHeaderRow,
)
from forms import (
    DetermineDescriptorTypesForm,
    DetermineOptionsForm,
    UploadForm
)


@bulk_resource.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    """Upload new resources in bulk with CSV file."""
    form = UploadForm()
    if form.validate_on_submit():
        csv_data = form.csv.data
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
            for column_name in header_row:
                csv_cell = CsvHeaderCell(data=column_name,
                                         csv_header_row=csv_header_row)
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
            db.session.commit()
            # TODO: Error catching if CSV is malformed.
            # TODO: Check that CSV file has "Name", "Address" headings
        return redirect(url_for('bulk_resource.review_descriptor_types'))
    return render_template('bulk_resource/upload.html', form=form)


@bulk_resource.route('/_upload', methods=['GET', 'POST'])
def upload_data():
    for arg in request.args:
        print arg
    print request.get_json()
    return 'hello'
    # print json.loads(request.data)
    # return redirect(url_for('bulk_resource.review_descriptor_types'))


@bulk_resource.route('/review-descriptor-types', methods=['GET', 'POST'])
@login_required
def review_descriptor_types():
    csv_container = CsvContainer.most_recent(user=current_user)
    if csv_container is None:
        abort(404)
    form = DetermineDescriptorTypesForm()
    if form.validate_on_submit():
        if form.navigation.data['submit_next']:
            for i, descriptor_type in enumerate(form.descriptor_types.data):
                csv_container.csv_header_row.csv_header_cells[i]\
                    .descriptor_type = descriptor_type
                db.session.add(
                    csv_container.csv_header_row.csv_header_cells[i]
                )
            db.session.commit()
            csv_container.predict_options()
            # TODO: Skip the second review step if there are no option
            # TODO: descriptor types.
            return redirect(url_for('bulk_resource.review_options'))
        elif form.navigation.data['submit_back']:
            db.session.delete(csv_container)
            return redirect(url_for('bulk_resource.upload'))
        elif form.navigation.data['submit_cancel']:
            db.session.delete(csv_container)
            return redirect(url_for('bulk_resource.upload'))

    # Add one text/option toggle for each CSV header.
    for i, header_cell in enumerate(csv_container.csv_header_row
                                    .csv_header_cells):
        form.descriptor_types.append_entry()
        form.descriptor_types[i].label = header_cell.data
        if header_cell.descriptor_type == 'option' or \
                header_cell.descriptor_type == 'text':
            form.descriptor_types[i].data = header_cell.descriptor_type

    return render_template('bulk_resource/review_descriptor_types.html',
                           csv_container=csv_container,
                           form=form)


@bulk_resource.route('/review-options', methods=['GET', 'POST'])
@login_required
def review_options():
    csv_container = CsvContainer.most_recent(user=current_user)
    if csv_container is None:
        abort(404)
    form = DetermineOptionsForm()
    if form.validate_on_submit():
        if form.navigation.data['submit_next']:
            options_indx = 0
            for i, header_cell in enumerate(csv_container.csv_header_row
                                            .csv_header_cells):
                if header_cell.descriptor_type == 'option':
                    header_cell.add_new_options_from_string(
                        form.options[options_indx].data
                    )
                    options_indx += 1
            return redirect(url_for('bulk_resource.review_options'))
        elif form.navigation.data['submit_back']:
            return redirect(url_for('bulk_resource.review_descriptor_types'))
        elif form.navigation.data['submit_cancel']:
            db.session.delete(csv_container)
            return redirect(url_for('bulk_resource.upload'))

    # Add one text/option toggle for each CSV header.
    j = 0
    for header_cell in csv_container.csv_header_row.csv_header_cells:
        if header_cell.descriptor_type == 'option':
            form.options.append_entry()
            form.options[j].label = header_cell.data
            form.options[j].label += ' (' + \
                                     header_cell.predicted_options_string() + \
                                     ')'
            form.options[j].data = header_cell.new_options_string()
            j += 1
    return render_template('bulk_resource/review-options.html',
                           csv_container=csv_container,
                           form=form)
