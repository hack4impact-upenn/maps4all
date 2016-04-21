from flask import abort, flash, render_template, redirect, url_for
from flask.ext.login import login_required
from sqlalchemy.exc import IntegrityError
from wtforms.fields import SelectField

from forms import (
    AddDescriptorOptionValueForm,
    EditDescriptorNameForm,
    EditDescriptorOptionValueForm,
    EditDescriptorSearchableForm,
    FixAllResourceOptionValueForm,
    NewDescriptorForm
)
from . import descriptor
from .. import db
from ..models import Descriptor, OptionAssociation


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
        descriptor.name = form.name.data
        if Descriptor.query.filter(Descriptor.name == form.name.data).first() \
                is not None:
            flash('Descriptor {} already exists.'.format(descriptor.name),
                  'form-error')
            return render_template('descriptor/manage_descriptor.html',
                                   desc=descriptor, form=form,
                                   is_option=is_option)

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
    return render_template('descriptor/manage_descriptor.html',
                           desc=descriptor, form=form, is_option=is_option)


@descriptor.route('/<int:desc_id>/option-values', methods=['GET', 'POST'])
@login_required
def change_option_values_index(desc_id):
    """Shows the page for changing descriptor's option values."""
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
    """Edt a descriptor's selected option value."""
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
    if descriptor is None:
        abort(404)
    old_value = descriptor.values[option_index]
    is_option = len(descriptor.values) != 0
    if not is_option:
        abort(404)
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
    choice_names = (['Remove this descriptor'] +
                    descriptor.values[:removed_index] +
                    descriptor.values[removed_index + 1:])
    choices = []
    for i in range(len(choice_names)):
        choices.append((i - 1, choice_names[i]))
    return choice_names, choices


def remove_value_from_db(descriptor, values, old_value):
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
    """Request deletion of a user's account."""
    descriptor = Descriptor.query.get(desc_id)
    if descriptor is None:
        abort(404)
    is_option = len(descriptor.values) != 0
    return render_template('descriptor/manage_descriptor.html',
                           desc=descriptor, is_option=is_option)


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
