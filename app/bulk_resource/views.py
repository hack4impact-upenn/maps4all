from datetime import datetime
import json
import geocoder

from flask import abort, jsonify, redirect, render_template, request, url_for
from flask.ext.login import current_user, login_required

from . import bulk_resource
from .. import db
from ..models import (
    CsvBodyCell,
    CsvBodyRow,
    CsvContainer,
    CsvHeaderCell,
    CsvHeaderRow,
    Descriptor,
    OptionAssociation,
    Resource,
    TextAssociation
)
from forms import (
    DetermineDescriptorTypesForm,
    DetermineOptionsForm,
    SaveCsvDataForm
)


@bulk_resource.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    """Upload new resources in bulk with CSV file."""
    return render_template('bulk_resource/upload.html')


@bulk_resource.route('/_upload', methods=['POST'])
def upload_data():
    # Extract CSV data from request object.
    for arg in request.form:
        post_data = arg
    post_data = json.loads(post_data)
    csv_data = post_data['csv_data']

    # Create new CSV container object to hold contents of CSV file.
    csv_container = CsvContainer(
        date_uploaded=datetime.now(),
        user=current_user,
        name_column_index=int(post_data['name_column_index']),
        address_column_index=int(post_data['address_column_index'])
    )

    # The first row of the CSV file contains the names of the columns.
    header_row = csv_data[0]
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
    for row in csv_data[1:]:
        csv_body_row = CsvBodyRow(csv_container=csv_container)
        for cell_data in row:
            csv_cell = CsvBodyCell(
                data=cell_data,
                csv_body_row=csv_body_row
            )
            db.session.add(csv_cell)
        db.session.add(csv_body_row)
    db.session.add(csv_container)
    db.session.commit()
    # TODO: If the only descriptors are the required ones, then no need to
    # TODO: review them.
    return jsonify(
        redirect=url_for('bulk_resource.review_descriptor_types')
    )


@bulk_resource.route('/review-descriptor-types', methods=['GET', 'POST'])
@login_required
def review_descriptor_types():
    csv_container = CsvContainer.most_recent(user=current_user)
    if csv_container is None:
        abort(404)
    form = DetermineDescriptorTypesForm()

    if form.validate_on_submit():
        if form.navigation.data['submit_next']:
            contains_options = False
            descriptor_types_iter = iter(form.descriptor_types.data)
            for i, header_cell in \
                    enumerate(csv_container.csv_header_row.csv_header_cells):
                if i not in csv_container.required_column_indices():
                    header_cell.descriptor_type = next(descriptor_types_iter)
                    if header_cell.descriptor_type == 'option':
                        contains_options = True
                    db.session.add(header_cell)
            db.session.commit()
            csv_container.predict_options()
            if contains_options:
                return redirect(url_for('bulk_resource.review_options'))
            return redirect(url_for('bulk_resource.save'))

        elif form.navigation.data['submit_back']:
            db.session.delete(csv_container)
            db.session.commit()
            return redirect(url_for('bulk_resource.upload'))

        elif form.navigation.data['submit_cancel']:
            db.session.delete(csv_container)
            db.session.commit()
            return redirect(url_for('bulk_resource.upload'))

    # Add one text/option toggle for each CSV header.
    j = 0
    for i, header_cell in enumerate(csv_container.csv_header_row
                                    .csv_header_cells):
        # Required columns are all 'text' descriptors. Their descriptor
        # type cannot be changed.
        if i not in csv_container.required_column_indices():
            form.descriptor_types.append_entry()
            form.descriptor_types[j].label = header_cell.data
            if header_cell.descriptor_type == 'option' or \
                    header_cell.descriptor_type == 'text':
                form.descriptor_types[j].data = header_cell.descriptor_type
            j += 1

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
            return redirect(url_for('bulk_resource.save'))
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
    return render_template('bulk_resource/review_options.html',
                           csv_container=csv_container,
                           form=form)


@bulk_resource.route('/save', methods=['GET', 'POST'])
@login_required
def save():
    csv_container = CsvContainer.most_recent(user=current_user)
    if csv_container is None:
        abort(404)
    form = SaveCsvDataForm()

    if form.validate_on_submit():
        # Temporary: Delete all descriptors and resources that are currently
        # in the database.
        Descriptor.query.delete()
        OptionAssociation.query.delete()
        Resource.query.delete()
        TextAssociation.query.delete()

        for i, header_cell in enumerate(
                csv_container.csv_header_row.csv_header_cells):
            if i not in csv_container.required_column_indices():
                values = set()
                if header_cell.descriptor_type == 'option':
                    for v in header_cell.predicted_options:
                        values.add(v)
                    for v in header_cell.new_options:
                        values.add(v)
                descriptor = Descriptor(
                    name=header_cell.data,
                    values=list(values),
                    is_searchable=True
                )
                db.session.add(descriptor)

        for row in csv_container.csv_rows:
            name = row.csv_body_cells[csv_container.name_column_index].data
            address = \
                row.csv_body_cells[csv_container.address_column_index].data
            g = geocoder.google(address)
            resource = Resource(
                name=name,
                address=address,
                latitude=g.latlng[0],
                longitude=g.latlng[1]
            )
            db.session.add(resource)
            for i, cell in enumerate(row.csv_body_cells):
                if i not in csv_container.required_column_indices():
                    descriptor_name = \
                        csv_container.csv_header_row.csv_header_cells[i].data
                    descriptor = Descriptor.query.filter_by(
                        name=descriptor_name
                    ).first()
                    values = list(descriptor.values)
                    assocValues = []
                    if len(descriptor.values) == 0:  # text descriptor
                        association_class = TextAssociation
                        assocValues.append(cell.data)
                        keyword = 'text'
                    else:  # option descriptor
                        association_class = OptionAssociation
                        for s in cell.data.split(';'):
                            assocValues.append(values.index(s))
                        keyword = 'option'
                    for value in assocValues:
                        arguments = {
                            'resource_id': resource.id,
                            'descriptor_id': descriptor.id,
                            keyword: value,
                            'resource': resource,
                            'descriptor': descriptor
                        }
                        new_association = association_class(**arguments)
                        db.session.add(new_association)
        db.session.delete(csv_container)
        db.session.commit()
        return redirect(url_for('single_resource.index'))
    return render_template('bulk_resource/save.html', form=form)
