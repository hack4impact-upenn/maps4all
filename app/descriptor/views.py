from flask import abort, flash, render_template, redirect, url_for, request
from flask.ext.login import login_required
from sqlalchemy.exc import IntegrityError
from wtforms.fields import SelectField
from flask_wtf.file import InputRequired

from forms import (
    AddDescriptorOptionValueForm,
    EditDescriptorNameForm,
    EditDescriptorOptionValueForm,
    EditDescriptorSearchableForm,
    FixAllResourceOptionValueForm,
    NewDescriptorForm,
    ChangeRequiredOptionDescriptorForm,
    RequiredOptionDescriptorMissingForm
)
from . import descriptor
from .. import db
from ..models import (
    Descriptor,
    OptionAssociation,
    Resource,
    RequiredOptionDescriptor,
    RequiredOptionDescriptorConstructor
)


@descriptor.route('/')
@login_required
def index():
    """View all resource descriptors."""
    descriptors = Descriptor.query.all()
    return render_template('descriptor/index.html',
                           descriptors=descriptors)


@descriptor.route('/new-descriptor', methods=['GET', 'POST'])
@login_required
def new_descriptor():
    """Create a new descriptor."""
    form = NewDescriptorForm()
    for i in range(10):
        form.option_values.append_entry()
    if form.validate_on_submit():
        values = []
        for v in form.option_values.data:
            if v is not None and len(v) != 0:
                values.append(v)
        descriptor = Descriptor(
            name=form.name.data,
            values=values,
            is_searchable=form.is_searchable.data
        )
        if Descriptor.query.filter(Descriptor.name == form.name.data).first() \
                is not None:
            flash('Descriptor {} already exists.'.format(descriptor.name),
                  'form-error')
        else:
            db.session.add(descriptor)
            try:
                db.session.commit()
                flash('Descriptor {} successfully created'
                      .format(descriptor.name),
                      'form-success')
                return redirect(url_for('descriptor.new_descriptor'))
            except IntegrityError:
                db.session.rollback()
                flash('Database error occurred. Please try again.',
                      'form-error')
    return render_template('descriptor/new_descriptor.html', form=form)


@descriptor.route('/<int:desc_id>', methods=['GET', 'POST'])
@login_required
def descriptor_info(desc_id):
    """Display the descriptor info."""
    descriptor = Descriptor.query.get(desc_id)
    if descriptor is None:
        abort(404)
    is_option = len(descriptor.values) != 0
    return render_template('descriptor/manage_descriptor.html',
                           desc=descriptor, is_option=is_option)


@descriptor.route('/<int:desc_id>/name', methods=['GET', 'POST'])
@login_required
def edit_name(desc_id):
    """Edit a descriptor's name."""
    descriptor = Descriptor.query.get(desc_id)
    if descriptor is None:
        abort(404)
    is_option = len(descriptor.values) != 0
    old_name = descriptor.name
    form = EditDescriptorNameForm()
    if form.validate_on_submit():
        if Descriptor.query.filter(Descriptor.name == form.name.data).first() \
                is not None:
            if old_name == form.name.data:
                flash('No change was made', 'form-error')
            else:
                flash('Descriptor {} already exists.'.format(form.name.data),
                    'form-error')
            return render_template('descriptor/manage_descriptor.html',
                                   desc=descriptor, form=form,
                                   is_option=is_option)
        descriptor.name = form.name.data
        db.session.add(descriptor)
        try:
            db.session.commit()
            flash('Name for descriptor {} successfully changed to {}.'
                  .format(old_name, descriptor.name),
                  'form-success')
        except IntegrityError:
            db.session.rollback()
            flash('Database error occurred. Please try again.', 'form-error')
        return render_template('descriptor/manage_descriptor.html',
                               desc=descriptor, is_option=is_option)
    form.name.data = descriptor.name
    return render_template('descriptor/manage_descriptor.html',
                           desc=descriptor, form=form, is_option=is_option)


@descriptor.route('/<int:desc_id>/searchable', methods=['GET', 'POST'])
@login_required
def edit_searchable(desc_id):
    """Edit a descriptor's searchability."""
    descriptor = Descriptor.query.get(desc_id)
    if descriptor is None:
        abort(404)
    is_option = len(descriptor.values) != 0
    old_value = descriptor.is_searchable
    form = EditDescriptorSearchableForm()
    if form.validate_on_submit():
        descriptor.is_searchable = form.is_searchable.data
        db.session.add(descriptor)
        try:
            db.session.commit()
            flash('Searchability successfully changed from {} to {}.'
                  .format(old_value, descriptor.is_searchable),
                  'form-success')
            return render_template('descriptor/manage_descriptor.html',
                                   desc=descriptor, is_option=is_option)
        except IntegrityError:
            db.session.rollback()
            flash('Database error occurred. Please try again.', 'form-error')
    form.is_searchable.data = old_value
    return render_template('descriptor/manage_descriptor.html',
                           desc=descriptor, form=form, is_option=is_option)


@descriptor.route('/<int:desc_id>/option-values', methods=['GET', 'POST'])
@login_required
def change_option_values_index(desc_id):
    """Shows the page to add/edit/remove a descriptor's option values."""
    descriptor = Descriptor.query.get(desc_id)
    if descriptor is None:
        abort(404)
    is_option = len(descriptor.values) != 0
    if not is_option:
        abort(404)
    form = AddDescriptorOptionValueForm()
    if form.validate_on_submit():
        values = descriptor.values[:]
        if form.value.data in values:
            flash('Value {} already exists'.format(form.value.data),
                  'form-error')
            return render_template('descriptor/manage_descriptor.html',
                                   desc=descriptor, is_option=is_option,
                                   desc_id=desc_id, form=form)

        values.append(form.value.data)
        descriptor.values = values
        db.session.add(descriptor)
        try:
            db.session.commit()
            flash('Value {} successfully added.'.format(form.value.data),
                  'form-success')
            form.value.data = ''
        except IntegrityError:
            db.session.rollback()
            flash('Database error occurred. Please try again.', 'form-error')
    return render_template('descriptor/manage_descriptor.html',
                           desc=descriptor, is_option=is_option,
                           desc_id=desc_id, form=form)


@descriptor.route('/<int:desc_id>/option-values/edit/<int:option_index>',
                  methods=['GET', 'POST'])
@login_required
def edit_option_value(desc_id, option_index):
    """Edit a descriptor's selected option value."""
    descriptor = Descriptor.query.get(desc_id)
    if descriptor is None:
        abort(404)
    is_option = len(descriptor.values) != 0
    form = EditDescriptorOptionValueForm()
    if not is_option:
        abort(404)
    if form.validate_on_submit():
        old_value = descriptor.values[option_index]
        values = descriptor.values[:]
        values[option_index] = form.value.data
        descriptor.values = values
        db.session.add(descriptor)
        try:
            db.session.commit()
            flash('Value {} for descriptor {} successfully changed to {}.'
                  .format(old_value, descriptor.name,
                          descriptor.values[option_index]),
                  'form-success')
            return redirect(url_for('descriptor.descriptor_info',
                                    desc_id=desc_id))
        except IntegrityError:
            db.session.rollback()
            flash('Database error occurred. Please try again.', 'form-error')
    else:
        form.value.data = descriptor.values[option_index]
    return render_template('descriptor/manage_descriptor.html',
                           desc=descriptor, is_option=is_option,
                           desc_id=desc_id, form=form)


@descriptor.route('/<int:desc_id>/option-values/remove/<int:option_index>',
                  methods=['GET', 'POST'])
@login_required
def remove_option_value(desc_id, option_index):
    """Remove a descriptor's selected option value."""
    descriptor = Descriptor.query.get(desc_id)
    if descriptor is None or len(descriptor.values) == 0:
        abort(404)
    old_value = descriptor.values[option_index]

    if len(descriptor.values) == 1:
        flash('Descriptor {} only has one value.'.format(descriptor.name),
              'form-error')
        return redirect(url_for('descriptor.change_option_values_index',
                                desc_id=desc_id))

    option_assocs = OptionAssociation.query.filter(db.and_(
        OptionAssociation.descriptor_id == desc_id,
        OptionAssociation.option == option_index
        )).all()

    choice_names, choices = generate_option_choices(descriptor, option_index)

    # If no resources are affected, just remove the option value.
    if len(option_assocs) == 0:
        # Index starting from 1 to skip 'Remove this descriptor'
        remove_value_from_db(descriptor, choice_names[1:], old_value)
        return redirect(url_for('descriptor.descriptor_info', desc_id=desc_id))

    # Create the select field for each resource.
    for oa in option_assocs:
        setattr(FixAllResourceOptionValueForm, oa.resource.name,
                SelectField('', coerce=int, choices=choices))
    form = FixAllResourceOptionValueForm()

    # Delete the dynamic fields after the form is instantiated
    for oa in option_assocs:
        delattr(FixAllResourceOptionValueForm, oa.resource.name)

    if form.validate_on_submit():
        for oa in option_assocs:
            choice = form[oa.resource.name].data
            # Case for 'Remove this descriptor'
            if choice == -1:
                db.session.delete(oa)
            else:
                oa.option = choice
                db.session.add(oa)

        # Index starting from 1 to skip 'Remove this descriptor'
        if remove_value_from_db(descriptor, choice_names[1:], old_value):
            return redirect(url_for('descriptor.descriptor_info',
                                    desc_id=desc_id))
    return render_template('descriptor/confirm_resources.html',
                           option_assocs=option_assocs, desc_id=desc_id,
                           desc=descriptor, option_index=option_index,
                           form=form)


def generate_option_choices(descriptor, removed_index):
    """Helper function to generate the option values for a SelectField."""
    choice_names = (['Remove this descriptor'] +
                    descriptor.values[:removed_index] +
                    descriptor.values[removed_index + 1:])
    choices = []
    for i in range(len(choice_names)):
        choices.append((i - 1, choice_names[i]))
    return choice_names, choices


def remove_value_from_db(descriptor, values, old_value):
    """Helper function to update the values an option can take."""
    descriptor.values = values
    db.session.add(descriptor)
    try:
        db.session.commit()
        flash('Value {} for descriptor {} successfully removed.'
              .format(old_value, descriptor.name),
              'form-success')
        return True
    except IntegrityError:
        db.session.rollback()
        flash('Database error occurred. Please try again.', 'form-error')
        return False


@descriptor.route('/<int:desc_id>/delete_request')
@login_required
def delete_descriptor_request(desc_id):
    """Shows the page for deletion of a descriptor."""
    descriptor = Descriptor.query.get(desc_id)
    if descriptor is None:
        abort(404)
    is_option = len(descriptor.values) != 0
    req_opt_desc = RequiredOptionDescriptor.query.all()[0]
    is_required = req_opt_desc.descriptor_id == descriptor.id
    return render_template('descriptor/manage_descriptor.html',
                           desc=descriptor, is_option=is_option,
                           is_required=is_required)


@descriptor.route('/<int:desc_id>/delete')
@login_required
def delete_descriptor(desc_id):
    """Deletes a descriptor."""
    descriptor = Descriptor.query.get(desc_id)
    if descriptor is None:
        abort(404)
    is_option = len(descriptor.values) != 0

    db.session.delete(descriptor)
    try:
        db.session.commit()
        flash('Successfully deleted descriptor %s.' % descriptor.name,
              'success')
    except IntegrityError:
            db.session.rollback()
            flash('Database error occurred. Please try again.', 'form-error')
            return render_template('descriptor/manage_descriptor.html',
                                   desc=descriptor, is_option=is_option)
    return redirect(url_for('descriptor.index'))

@descriptor.route('/change-required-option-descriptor', methods=['GET', 'POST'])
@login_required
def change_required_option_descriptor():
    descriptors = Descriptor.query.all()
    choices = []
    for d in descriptors:
        if d.values:
            choices.append((d.name, d.name))
    req_opt_desc = RequiredOptionDescriptor.query.all()[0]
    current_name = ""
    if req_opt_desc.descriptor_id != -1:
        descriptor = Descriptor.query.filter_by(
            id=req_opt_desc.descriptor_id
        ).first()
        if descriptor is not None:
            current_name = descriptor.name
    if current_name != "":
        setattr(
            ChangeRequiredOptionDescriptorForm,
            'descriptor',
            SelectField(
                'Option Descriptor',
                choices=choices,
                validators=[InputRequired()],
                default=current_name)
        )
        form = ChangeRequiredOptionDescriptorForm()
        if form.validate_on_submit():
            RequiredOptionDescriptorConstructor.query.delete()
            db.session.commit()
            desc = Descriptor.query.filter_by(
                name=form.descriptor.data
            ).first()
            if desc is not None:
                req_opt_desc_const = RequiredOptionDescriptorConstructor(name=desc.name, values=desc.values)
                db.session.add(req_opt_desc_const)
                db.session.commit()
            return redirect(url_for('descriptor.review_required_option_descriptor'))
    else:
        form = None
    return render_template(
            'descriptor/change_required_option_descriptor.html',
            form=form
    )

@descriptor.route('/review-required-option-descriptor', methods=['GET', 'POST'])
@login_required
def review_required_option_descriptor():
    req_opt_desc_const = RequiredOptionDescriptorConstructor.query.all()[0]
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
    if request.method == 'POST':
        if len(form.resources.data) < len(missing_resources):
            flash('Error: You must choose an option for each resource. Please try again.', 'form-error')
        else:
            for j, r_name in enumerate(missing_resources):
                resource = Resource.query.filter_by(
                    name=r_name
                ).first()
                if resource is not None:
                    for val in form.resources.data[j]:
                        new_association = OptionAssociation(
                                            resource_id=resource.id,
                                            descriptor_id=descriptor.id,
                                            option=descriptor.values.index(val),
                                            resource=resource,
                                            descriptor=descriptor)
                        db.session.add(new_association)
                RequiredOptionDescriptor.query.delete()
                req_opt_desc = RequiredOptionDescriptor(descriptor_id=descriptor.id)
                db.session.add(req_opt_desc)
                db.session.commit()
            return redirect(url_for('descriptor.index'))
    for j, r_name in enumerate(missing_resources):
        form.resources.append_entry()
        form.resources[j].label = r_name
        form.resources[j].choices = [(v, v) for v in req_opt_desc_const.values]
    return render_template('descriptor/review_required_option_descriptor.html', form=form)

