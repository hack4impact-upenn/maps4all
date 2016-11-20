from datetime import datetime
import json
import geocoder

from flask import abort, jsonify, redirect, render_template, request, url_for, flash
from flask.ext.login import current_user, login_required

from flask_wtf.file import (
    InputRequired
)
from wtforms.fields import (
    FieldList,
    RadioField,
    FormField
)
from flask.ext.wtf import Form

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
    RequiredOptionDescriptor,
    RequiredOptionDescriptorConstructor,
    TextAssociation
)
from forms import (
    DetermineRequiredOptionDescriptorForm,
    RequiredOptionDescriptorMissingForm,
    DetermineDescriptorTypesForm,
    DetermineOptionsForm,
    NavigationForm,
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
        address_column_index=int(post_data['address_column_index']),
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
            return redirect(url_for('bulk_resource.get_required_option_descriptor'))

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
            return redirect(url_for('bulk_resource.get_required_option_descriptor'))
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

@bulk_resource.route('/get-required-option-descriptor', methods=['GET', 'POST'])
@login_required
def get_required_option_descriptor():
    csv_container = CsvContainer.most_recent(user=current_user)
    form = DetermineRequiredOptionDescriptorForm()
    if form.validate_on_submit():
        if form.navigation.data['submit_back']:
            return redirect(url_for('bulk_resource.review_options'))
        elif form.navigation.data['submit_cancel']:
            return redirect(url_for('bulk_resource.upload'))
        descriptor = Descriptor.query.filter_by(
            name=form.required_option_descriptor.data
        ).first()
        RequiredOptionDescriptorConstructor.query.delete()
        db.session.commit()
        if descriptor is not None and not descriptor.values:
            req_opt_desc_const = RequiredOptionDescriptorConstructor(name=descriptor.name, values=descriptor.values)
            db.session.add(req_opt_desc_const)
            db.session.commit()
            return redirect(url_for('bulk_resource.review_required_option_descriptor'))
        for header_cell in csv_container.csv_header_row.csv_header_cells:
            if header_cell.data == form.required_option_descriptor.data and header_cell.descriptor_type == 'option':
                values = []
                for v in header_cell.predicted_options:
                    values.append(v)
                for v in header_cell.new_options:
                    values.append(v)
                req_opt_desc_const = RequiredOptionDescriptorConstructor(name=header_cell.data, values=values)
                db.session.add(req_opt_desc_const)
                return redirect(url_for('bulk_resource.review_required_option_descriptor'))
        flash('Error: no such option descriptor. Please try again.', 'form-error')
    req_opt_desc = RequiredOptionDescriptor.query.all()[0]
    desc_name = ""
    if req_opt_desc.id != -1:
        descriptor = Descriptor.query.filter_by(
            id=req_opt_desc.id
        ).first()
        if descriptor is not None:
            desc_name = descriptor.name
    form.required_option_descriptor.data = desc_name
    return render_template(
                'bulk_resource/get_required_option_descriptor.html',
                form=form
    )

@bulk_resource.route('/review_required_option_descriptor', methods=['GET', 'POST'])
@login_required
def review_required_option_descriptor():
    csv_container = CsvContainer.most_recent(user=current_user)
    req_opt_desc_const = RequiredOptionDescriptorConstructor.query.all()[0]
    setattr(RequiredOptionDescriptorMissingForm, 'resources', FieldList(RadioField(choices=[(v, v) for v in req_opt_desc_const.values], validators=[InputRequired()])))
    form = RequiredOptionDescriptorMissingForm()
    missing_resources = []
    resources = Resource.query.all()
    descriptor = Descriptor.query.filter_by(
        name=req_opt_desc_const.name
    ).first()
    for r in resources:
        if descriptor is None:
            missing_resources.append(r.name)
        else:
            option_association = OptionAssociation.query.filter_by(
                resource_id = r.id,
                descriptor_id=descriptor.id
            ).first()
            if option_association is None:
                missing_resources.append(r.name)
    req_opt_desc_index = -1
    for i, header_cell in enumerate(csv_container.csv_header_row.csv_header_cells):
        if header_cell.data == req_opt_desc_const.name:
            req_opt_desc_index = i
            break
    for row in csv_container.csv_rows:
        if req_opt_desc_index == -1 or len(row.csv_body_cells[req_opt_desc_index].data) == 0:
            missing_resources.append(row.csv_body_cells[csv_container.name_column_index].data)
    if form.validate_on_submit():
        if form.navigation.data['submit_back']:
            return redirect(url_for('bulk_resource.get_required_option_descriptor'))
        elif form.navigation.data['submit_cancel']:
            return redirect(url_for('bulk_resource.upload'))
        req_opt_desc_const.missing_dict = {}
        resources_values_iter = iter(form.resources.data)
        for j, r_name in enumerate(missing_resources):
            req_opt_desc_const.missing_dict[r_name] = next(resources_values_iter)
        db.session.commit()
        return redirect(url_for('bulk_resource.save'))
    for j, r_name in enumerate(missing_resources):
        form.resources.append_entry()
        form.resources[j].label = r_name
    return render_template('bulk_resource/review_required_option_descriptor.html', form=form)

@bulk_resource.route('/save', methods=['GET', 'POST'])
@login_required
def save():
    csv_container = CsvContainer.most_recent(user=current_user)
    req_opt_desc_const = RequiredOptionDescriptorConstructor.query.all()[0]
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
                    if len(descriptor.values) == 0:  # text descriptor
                        association_class = TextAssociation
                        value = cell.data
                        keyword = 'text'
                    else:  # option descriptor
                        association_class = OptionAssociation
                        value = values.index(cell.data)
                        keyword = 'option'
                    arguments = {
                        'resource_id': resource.id,
                        'descriptor_id': descriptor.id,
                        keyword: value,
                        'resource': resource,
                        'descriptor': descriptor
                    }
                    new_association = association_class(**arguments)
                    db.session.add(new_association)
        required_option_descriptor = Descriptor.query.filter_by(
            name=req_opt_desc_const.name
        ).first()
        if required_option_descriptor is None:
            required_option_descriptor = Descriptor(name=req_opt_desc_const.name, values=req_opt_desc_const.values, is_searchable=True)
            db.session.add(required_option_descriptor)
            db.session.commit()
        for r_name in req_opt_desc_const.missing_dict.keys():
            resource = Resource.query.filter_by(
                name=r_name
            ).first()
            if resources is not None:
                new_association = OptionAssociation(resource_id=resource.id, descriptor_id=required_option_descriptor.id, option=required_option_descriptor.values.index(req_opt_desc_const.missing_dict[r_name]), resource=resource, descriptor=descriptor)
                db.session.add(new_association)
        db.session.delete(req_opt_desc_const)
        db.session.delete(csv_container)
        db.session.commit()
        return redirect(url_for('single_resource.index'))
    return render_template('bulk_resource/save.html', form=form)
