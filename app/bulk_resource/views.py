from datetime import datetime
import json
import geocoder
import time
import os

from flask import abort, jsonify, redirect, render_template, request, url_for, flash
from flask.ext.login import current_user, login_required

from flask_wtf.file import (
    InputRequired
)
from wtforms.fields import (
    FieldList,
    RadioField,
    FormField,
    SelectMultipleField
)
from flask.ext.wtf import Form

from app import csrf
from . import bulk_resource
from .. import db
from ..models import (
    CsvStorage,
    CsvRow,
    CsvDescriptor,
    CsvDescriptorRemove,
    GeocoderCache,
    Descriptor,
    OptionAssociation,
    Rating,
    Resource,
    RequiredOptionDescriptor,
    RequiredOptionDescriptorConstructor,
    Suggestion,
    TextAssociation
)
from .forms import (
    DetermineRequiredOptionDescriptorForm,
    RequiredOptionDescriptorMissingForm,
    DetermineDescriptorTypesForm,
    DetermineOptionsForm,
    NavigationForm,
    SaveCsvDataForm
)
from .helpers import (
    validate_address
)


@csrf.exempt
@bulk_resource.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    """Upload new resources in bulk with CSV file."""
    return render_template('bulk_resource/upload.html')


''' Processes each Deferred Ajax request '''
@csrf.exempt
@bulk_resource.route('/_upload', methods=['POST'])
def upload_row():
    data = json.loads(request.form['json'])

    # Store CSV fields as descriptors
    if data['action'] == 'fields-reset': # Reset operation
        try:
            fields = data['fields']

            # Temporary storage area for CSV data
            csv_storage = CsvStorage(
                date_uploaded=datetime.now(),
                user=current_user,
                action='reset',
            )

            # Store new descriptors
            fields = [f.strip() for f in fields if
                f.strip() and f.strip() != 'Name' and f.strip() != 'Address']
            for f in fields:
                desc = CsvDescriptor(
                    csv_storage=csv_storage,
                    name=f,
                    values=set(),
                )
                db.session.add(desc)
            db.session.add(csv_storage)
            db.session.commit()
            return jsonify({
                "status": "Success",
                "message": "Successfully added fields",
                })
        except:
            db.session.rollback()
            abort(404)
    if data['action'] == 'fields-update': # Update operation
        try:
            fields = data['fields']
            csv_storage = CsvStorage(
                date_uploaded=datetime.now(),
                user=current_user,
                action='update',
            )

            # get old fields
            descriptors = Descriptor.query.all()
            descriptors = dict([(d.name, d) for d in descriptors])
            old_d = list(descriptors.keys())

            # compare with new fields
            new_d = [f.strip() for f in fields if
                f.strip() and f.strip() != 'Name' and f.strip() != 'Address']

            # store descriptors to remove
            removed = set(old_d) - set(new_d)
            for f in removed:
                old_desc = Descriptor.query.filter_by(
                    name=f
                ).first()
                desc = CsvDescriptorRemove(
                    csv_storage=csv_storage,
                    descriptor_id=old_desc.id,
                    name=old_desc.name,
                )
                db.session.add(desc)

            # store old descriptors not removed
            keep = set(old_d).intersection(set(new_d))
            for f in keep:
                existing_desc = descriptors.get(f)
                existing_type = 'option' if existing_desc.values else 'text'
                # CSVDescriptor only stores values from CSV, not existing values in app
                desc = CsvDescriptor(
                    csv_storage=csv_storage,
                    name=f,
                    values=set(),
                    descriptor_id=existing_desc.id,
                    descriptor_type=existing_type,
                )
                db.session.add(desc)

            # store new descriptors
            added = set(new_d) - set(old_d)
            for f in added:
                desc = CsvDescriptor(
                    csv_storage=csv_storage,
                    name=f,
                    values=set(),
                )
                db.session.add(desc)

            db.session.add(csv_storage)
            db.session.commit()
            return jsonify({
                "status": "Success",
                "message": "Successfully added fields"
                })
        except:
            db.session.rollback()
            abort(404)

    # Store CSV rows
    if data['action'] == 'reset-update': # Reset operation
        try:
            row = data['row']
            clean_row = {k.strip():v.strip() for k, v in row.items()}

            # Validate addresses
            address = clean_row['Address']
            # print(validate_address(data, address))
            gstatus = validate_address(data, address)
            if gstatus != 'OK':
                msg = 'Address cannot be geocoded due to ' + gstatus + ": " + address
                return jsonify({
                    "status": "Error",
                    "message": msg
                    })

            csv_storage = CsvStorage.most_recent(user=current_user)
            if csv_storage is None:
                abort(404)

            csv_row = CsvRow(
                csv_storage=csv_storage,
                data=clean_row,
            )
            db.session.add(csv_row)
            db.session.commit()
            return jsonify({
                "status": "Success",
                "message": "Successfully added row"
                })
        except:
            db.session.rollback()
            abort(404)
    if data['action'] == 'update': # Update operation
        try:
            row = data['row']
            clean_row = {k.strip():v.strip() for k, v in row.items()}

            # Validate addresses
            address = clean_row['Address']
            gstatus = validate_address(data, address)
            if gstatus != 'OK':
                msg = 'Address cannot be geocoded due to ' + gstatus + ": " + address
                return jsonify({
                    "status": "Error",
                    "message": msg
                    })

            csv_storage = CsvStorage.most_recent(user=current_user)
            if csv_storage is None:
                abort(404)

            csv_row = CsvRow(
                csv_storage=csv_storage,
                data=clean_row
            )
            # See if resource already exists
            existing_resource = Resource.query.filter_by(
                name=row['Name']
            ).first()
            if existing_resource is not None:
                csv_row.resource_id = existing_resource.id

            db.session.add(csv_row)
            db.session.commit()
            return jsonify({
                "status": "Success",
                "message": "Successfully added row"
                })
        except:
            db.session.rollback()
            abort(404)

    # Done processing CSV, move onto next step
    if data['action'] == 'finished':
        csv_storage = CsvStorage.most_recent(user=current_user)
        if csv_storage is None:
            abort(404)

        if len(csv_storage.csv_rows) == 0:
            return jsonify({
                "status": "Error",
                "message": 'No resources to update from CSV'
                })

        return jsonify(
            redirect=url_for('bulk_resource.set_descriptor_types')
        )


''' Sets each descriptor in the CSV to be an option or a text descriptor '''
@bulk_resource.route('/set-descriptor-types', methods=['GET', 'POST'])
@login_required
def set_descriptor_types():
    csv_storage = CsvStorage.most_recent(user=current_user)
    if csv_storage is None:
        db.session.rollback()
        abort(404)
    form = DetermineDescriptorTypesForm()

    if form.validate_on_submit():
        if form.navigation.data['submit_next']:
            contains_options = False
            descriptor_types_iter = iter(form.descriptor_types.data)
            # Set the chosen descriptor types for the new descriptors in the CSV
            for desc in csv_storage.csv_descriptors:
                if not desc.descriptor_id:
                    desc.descriptor_type = next(descriptor_types_iter)
                    db.session.add(desc)
                if desc.descriptor_type == 'option':
                    contains_options = True
            db.session.commit()

            # Find the option descriptor values in the CSV if there are option
            # descriptors
            if contains_options:
                csv_storage.set_desc_values()
                return redirect(url_for('bulk_resource.review_desc_options'))
            return redirect(url_for('bulk_resource.set_required_option_descriptor'))

        elif form.navigation.data['submit_back']:
            db.session.delete(csv_storage)
            db.session.commit()
            return redirect(url_for('bulk_resource.upload'))

        elif form.navigation.data['submit_cancel']:
            db.session.delete(csv_storage)
            db.session.commit()
            return redirect(url_for('bulk_resource.upload'))

    # Add one text/option toggle for each new CSV descriptor
    num = 0
    for desc in csv_storage.csv_descriptors:
        # We don't allow setting a new type for existing descriptors
        if not desc.descriptor_id:
            form.descriptor_types.append_entry()
            form.descriptor_types[num].label = desc.name
            if desc.descriptor_type == 'option' or \
                    desc.descriptor_type == 'text':
                form.descriptor_types[num].data = desc.descriptor_type
            num += 1

    # Remove auto form label
    form.descriptor_types.label = ''

    # Show what type is for each existing descriptor (but don't allow to change)
    # Also show which ones to remove
    existing_descs = []
    remove_descs = []
    if csv_storage.action == 'update':
        remove_descs = [d.name for d in csv_storage.csv_descriptors_remove]
        existing_descs = [d for d in Descriptor.query.all() if d.name not in remove_descs]

    return render_template('bulk_resource/set_descriptor_types.html',
                           form=form, existing_descs=existing_descs,
                           num=num, remove_descs=remove_descs)


''' If there are option descriptors in the CSV, display the option values parsed
from the CSV for verification '''
@bulk_resource.route('/review-desc-options', methods=['GET', 'POST'])
@login_required
def review_desc_options():
    csv_storage = CsvStorage.most_recent(user=current_user)
    if csv_storage is None:
        db.session.rollback()
        abort(404)
    form = DetermineOptionsForm()

    if form.validate_on_submit():
        if form.navigation.data['submit_next']:
            return redirect(url_for('bulk_resource.set_required_option_descriptor'))
        elif form.navigation.data['submit_back']:
            return redirect(url_for('bulk_resource.set_descriptor_types'))
        elif form.navigation.data['submit_cancel']:
            db.session.delete(csv_storage)
            db.session.commit()
            return redirect(url_for('bulk_resource.upload'))

    # New option descriptors found in the CSV
    new_opt_descs = [desc for desc in csv_storage.csv_descriptors
                 if desc.descriptor_type == 'option' and not desc.descriptor_id]

    # Old option descriptors found in the app
    old_opt_descs = []
    if csv_storage.action == 'update':
        old_opt_descs_csv = [desc for desc in csv_storage.csv_descriptors
                     if desc.descriptor_type == 'option' and desc.descriptor_id]
        for d in old_opt_descs_csv:
            old_d = Descriptor.query.filter_by(
                id=d.descriptor_id
            ).first()
            old_opt_descs.append((d, old_d))
        old_opt_descs = dict(old_opt_descs)
    return render_template('bulk_resource/review_desc_options.html',
                           new_opt_descs=new_opt_descs,
                           old_opt_descs=old_opt_descs,
                           form=form)


''' Choose one option descriptor to be the required option descriptor.
Can only select from option descriptors in the CSV or the existing required
option descriptor if any.'''
@bulk_resource.route('/set-required-option-descriptor', methods=['GET', 'POST'])
@login_required
def set_required_option_descriptor():
    csv_storage = CsvStorage.most_recent(user=current_user)
    if csv_storage is None:
        db.session.rollback()
        abort(404)
    form = DetermineRequiredOptionDescriptorForm()

    # For form submission
    if request.method == 'POST':
        if form.navigation.data['submit_back']:
            return redirect(url_for('bulk_resource.review_desc_options'))
        elif form.navigation.data['submit_cancel']:
            db.session.delete(csv_storage)
            db.session.commit()
            return redirect(url_for('bulk_resource.upload'))
        elif form.required_option_descriptor.data == "":
            flash('Error: You must select a required option descriptor. Please try again.', 'form-error')
        else:
            # Store the selected required option descriptor
            RequiredOptionDescriptorConstructor.query.delete()
            db.session.commit()

            # See if required option descriptor is in CSV
            for desc in csv_storage.csv_descriptors:
                if desc.name == form.required_option_descriptor.data and desc.descriptor_type == 'option':
                    values = desc.values
                    # see if existing descriptor
                    if csv_storage.action == 'update':
                        if desc.descriptor_id:
                            descriptor = Descriptor.query.filter_by(
                                id=desc.descriptor_id
                            ).first()
                            for v in descriptor.values:
                                values.add(v)
                    req_opt_desc_const = RequiredOptionDescriptorConstructor(
                        name=desc.name,
                        values=desc.values
                    )
                    db.session.add(req_opt_desc_const)
                    db.session.commit()
                    return redirect(url_for('bulk_resource.validate_required_option_descriptor'))

            # If not in CSV, see if it is existing required option descriptor
            req_opt_desc = RequiredOptionDescriptor.query.all()
            if req_opt_desc:
                req_opt_desc = req_opt_desc[0]
                if req_opt_desc.descriptor_id != -1:
                    descriptor = Descriptor.query.filter_by(
                        id=req_opt_desc.descriptor_id
                    ).first()
                    if descriptor is not None and descriptor.name == form.required_option_descriptor.data:
                        req_opt_desc_const = RequiredOptionDescriptorConstructor(
                            name=descriptor.name,
                            values=descriptor.values
                        )
                        db.session.add(req_opt_desc_const)
                        db.session.commit()
                        return redirect(url_for('bulk_resource.validate_required_option_descriptor'))
            # If no descriptor found
            flash('Error: No required option descriptor. Please try again.', 'form-error')

    descriptors = []
    # If there is an existing required option descriptor, then make it
    # the default choice
    req_name = ''
    remove_descs = [d.name for d in csv_storage.csv_descriptors_remove]
    if csv_storage.action == 'update':
        req_opt_desc = RequiredOptionDescriptor.query.all()
        if req_opt_desc:
            req_opt_desc = req_opt_desc[0]
            if req_opt_desc.descriptor_id != -1:
                descriptor = Descriptor.query.filter_by(
                    id=req_opt_desc.descriptor_id
                ).first()
                if descriptor is not None and descriptor.name not in remove_descs:
                    req_name = descriptor.name
                    descriptors.append(req_name)

    # Collect all option descriptors in the CSV to display as choices in the
    # SelectField.
    for desc in csv_storage.csv_descriptors:
        if desc.descriptor_type == 'option' and desc.name != req_name:
            descriptors.append(desc.name)

    # No existing required option descriptor and no option descriptors in CSV,
    # then no possible required option descriptor
    if len(descriptors) == 0:
        return redirect(url_for('bulk_resource.save_csv'))

    form.required_option_descriptor.choices = [(d, d) for d in descriptors]
    return render_template(
                'bulk_resource/get_required_option_descriptor.html',
                current=req_name,
                form=form
    )


''' If there are resources that don't have the selected required option descriptor value set,
enforce that they are updated to have the required option descriptor'''
@bulk_resource.route('/validate-required-option-descriptor', methods=['GET', 'POST'])
@login_required
def validate_required_option_descriptor():
    csv_storage = CsvStorage.most_recent(user=current_user)
    if csv_storage is None:
        db.session.rollback()
        abort(404)
    req_opt_desc_const = RequiredOptionDescriptorConstructor.query.all()[0]
    req_opt_desc = req_opt_desc_const.name
    missing_resources = set()
    form = RequiredOptionDescriptorMissingForm()

    # Find resources in the CSV that lack association with chosen required option
    # descriptor
    csv_resources = set()
    for row in csv_storage.csv_rows:
        csv_resources.add(row.data['Name'])
        if req_opt_desc not in row.data or row.data[req_opt_desc].strip() == '':
            missing_resources.add(row.data['Name'])

    # Find all existing resources that lack an
    # association with the chosen required option descriptor
    if csv_storage.action == 'update':
        # Check if there is a required option descriptor already
        curr_req_opt_desc = RequiredOptionDescriptor.query.all()
        curr_req = ''
        if curr_req_opt_desc:
            curr_req_opt_desc = curr_req_opt_desc[0]
            if curr_req_opt_desc.descriptor_id != -1:
                req_descriptor = Descriptor.query.filter_by(
                    id=curr_req_opt_desc.descriptor_id
                ).first()
                if req_descriptor is not None:
                    curr_req = req_descriptor.name

        resources = Resource.query.all()
        for r in resources:
            # If no previous required option descriptor
            # or new required is not same as old
            if curr_req == '' or req_opt_desc != curr_req:
                if r.name not in csv_resources:
                    missing_resources.add(r.name)
            # Same required option descriptor
            elif req_opt_desc == curr_req:
                if r.name in missing_resources:
                    missing_resources.remove(r.name)

    # For form submission
    if request.method == 'POST':
        if form.navigation.data['submit_back']:
            return redirect(url_for('bulk_resource.set_required_option_descriptor'))
        elif form.navigation.data['submit_cancel']:
            db.session.delete(csv_storage)
            db.session.commit()
            return redirect(url_for('bulk_resource.upload'))
        # Create a dictionary for storing the chosen option value for each
        # resource that previously lacked an association with the descriptor.
        req_opt_desc_const.missing_dict = {}
        if len(form.resources.data) < len(missing_resources):
            flash('Error: You must choose an option for each resource. Please try again.', 'form-error')
        else:
            for num, name in enumerate(missing_resources):
                req_opt_desc_const.missing_dict[name] = form.resources.data[num]
            db.session.commit()
            return redirect(url_for('bulk_resource.save_csv'))

    # All resources have the required option descriptor value set
    if len(missing_resources) == 0:
        req_opt_desc_const.missing_dict = {}
        return redirect(url_for('bulk_resource.save_csv'))

    # For every resource lacking an association with the chosen descriptor,
    # create a SelectField in the form's FieldList with the choices for the
    # descriptor.
    for num, name in enumerate(missing_resources):
        form.resources.append_entry()
        form.resources[num].label = name
        form.resources[num].choices = [(v, v) for v in req_opt_desc_const.values]

    # Remove auto form label
    form.resources.label = ''

    return render_template(
                'bulk_resource/review_required_option_descriptor.html',
                form=form,
                required=req_opt_desc,
    )


''' Last step in CSV workflow to update the resource and descriptor data models'''
@bulk_resource.route('/save-csv', methods=['GET', 'POST'])
@login_required
def save_csv():
    csv_storage = CsvStorage.most_recent(user=current_user)
    if csv_storage is None:
        db.session.rollback()
        abort(404)
    form = SaveCsvDataForm()

    if form.validate_on_submit():
        if form.data['submit_back']:
            req_opt_desc_const = RequiredOptionDescriptorConstructor.query.all()
            if not req_opt_desc_const:
                return redirect(url_for('bulk_resource.set_descriptor_types'))
            elif req_opt_desc_const[0].missing_dict:
                return redirect(url_for('bulk_resource.validate_required_option_descriptor'))
            else:
                return redirect(url_for('bulk_resource.set_required_option_descriptor'))
        elif form.data['submit_cancel']:
            db.session.delete(csv_storage)
            db.session.commit()
            return redirect(url_for('bulk_resource.upload'))

        RequiredOptionDescriptor.query.delete()
        if csv_storage.action == 'reset':
            OptionAssociation.query.delete()
            TextAssociation.query.delete()
            # on delete suggestions linked to resources
            Suggestion.query.filter(Suggestion.resource_id != None).delete()
            Rating.query.delete()
            Descriptor.query.delete()
            Resource.query.delete()

        # Create/Update descriptors
        for desc in csv_storage.csv_descriptors:
            # if existing descriptor, add new descriptor values
            if csv_storage.action == 'update' and desc.descriptor_id:
                if desc.descriptor_type == 'option':
                    existing_descriptor = Descriptor.query.filter_by(
                        id=desc.descriptor_id
                    ).first()
                    values = existing_descriptor.values
                    values.extend(desc.values)
                    existing_descriptor.values = list(set(values))
                    db.session.add(existing_descriptor)
            else:
                descriptor = Descriptor(
                    name=desc.name,
                    values=list(desc.values),
                    is_searchable=True,
                )
                db.session.add(descriptor)

        # Remove descriptors not in the CSV
        for desc in csv_storage.csv_descriptors_remove:
            d = Descriptor.query.get(desc.descriptor_id)
            if d is None:
                db.session.rollback()
                abort(404)
            db.session.delete(d)

        # Create/update rows and descriptor associations
        for row in csv_storage.csv_rows:
            if csv_storage.action == 'update' and row.resource_id:
                resource = Resource.query.filter_by(
                    id=row.resource_id
                ).first()
                address = row.data['Address']
                if resource.address != address:
                    resource.address = address
                    cached = GeocoderCache.query.filter_by(
                        address=address
                    ).first()
                    if cached is None:
                        db.session.rollback()
                        abort(404)
                    resource.latitude = cached.latitude
                    resource.longitude = cached.longitude
                    db.session.add(resource)
            else:
                name = row.data['Name']
                address = row.data['Address']
                cached = GeocoderCache.query.filter_by(
                    address=address
                ).first()
                if cached is None:
                    db.session.rollback()
                    abort(404)
                resource = Resource(
                    name=name,
                    address=address,
                    latitude=cached.latitude,
                    longitude=cached.longitude
                )
                db.session.add(resource)

            # Loop through descriptors on the resource rows
            for key in row.data:
                if key and key != 'Name' and key != 'Address':
                    descriptor = Descriptor.query.filter_by(
                        name=key
                    ).first()
                    values = list(descriptor.values)
                    assocValues = []
                    if len(descriptor.values) == 0:  # text descriptor
                        association_class = TextAssociation
                        keyword = 'text'
                        # see if same descriptor already exists
                        if csv_storage.action == 'update':
                            text_association = TextAssociation.query.filter_by(
                                resource_id=resource.id,
                                descriptor_id=descriptor.id,
                            ).first()
                            if text_association is None:
                                assocValues.append(row.data[key])
                            # Just update text value if only text changed
                            elif text_association.text != row.data[key]:
                                text_association.text = row.data[key]
                                db.session.add(text_association)
                        else:
                            assocValues.append(row.data[key])
                    else:  # option descriptor
                        association_class = OptionAssociation
                        keyword = 'option'
                        curr_opts = []
                        for s in row.data[key].split(';'):
                            s = s.strip()
                            if s in values:
                                curr_opts.append(values.index(s))
                        # see if same descriptor already exists
                        if csv_storage.action == 'update':
                            option_associations = OptionAssociation.query.filter_by(
                                resource_id=resource.id,
                                descriptor_id=descriptor.id
                            )
                            if option_associations is None:
                                assocValues.extend(curr_opts)
                            else:
                                # Check if existing options same as new ones in CSV
                                old_opts = [opt.option for opt in option_associations]
                                if set(curr_opts) != set(old_opts):
                                    # If options different, delete existing and add new ones after
                                    for o in option_associations:
                                        db.session.delete(o)
                                    assocValues.extend(curr_opts)
                        else:
                            assocValues.extend(curr_opts)

                    # Create new descriptor associations
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

        # Set required option descriptor
        req_opt_desc_const = RequiredOptionDescriptorConstructor.query.all()
        if req_opt_desc_const:
            req_opt_desc_const = req_opt_desc_const[0]
            required_option_descriptor = Descriptor.query.filter_by(
                name=req_opt_desc_const.name
            ).first()
            if required_option_descriptor is None:
                required_option_descriptor = Descriptor(
                                                name=req_opt_desc_const.name,
                                                dtype='option',
                                                values=req_opt_desc_const.values,
                                                is_searchable=True)
                db.session.add(required_option_descriptor)
            req_opt_desc = RequiredOptionDescriptor(descriptor_id=required_option_descriptor.id)

            # Add associations for the resources missing values for the required option descriptor
            if req_opt_desc_const.missing_dict:
                for name in list(req_opt_desc_const.missing_dict.keys()):
                    resource = Resource.query.filter_by(
                        name=name
                    ).first()
                    if resource is not None:
                        for val in req_opt_desc_const.missing_dict[name]:
                            new_association = OptionAssociation(
                                                resource_id=resource.id,
                                                descriptor_id=required_option_descriptor.id,
                                                option=required_option_descriptor.values.index(val),
                                                resource=resource, descriptor=required_option_descriptor)
                            db.session.add(new_association)
            db.session.delete(req_opt_desc_const)
            db.session.add(req_opt_desc)
        else:
            # No required option descriptor set, initialize to dummy
            req_opt_desc = RequiredOptionDescriptor(descriptor_id=-1)
            db.session.add(req_opt_desc)

        db.session.delete(csv_storage)
        try:
            db.session.commit()
        except:
            db.session.rollback()
            abort(404)
        return redirect(url_for('single_resource.index'))
    return render_template('bulk_resource/save.html', form=form)
