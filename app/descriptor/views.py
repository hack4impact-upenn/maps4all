from flask import abort, flash, render_template, redirect, url_for
from flask.ext.login import login_required

from forms import (
    EditDescriptorNameForm,
    EditDescriptorOptionValueForm,
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
        descriptor = Descriptor(name=form.name.data, values=values)
        if Descriptor.query.filter(Descriptor.name == form.name.data).first() \
                is not None:
            flash('Descriptor {} already exists.'.format(descriptor.name),
                  'form-error')
        else:
            db.session.add(descriptor)
            db.session.commit()
            flash('Descriptor {} successfully created'.format(descriptor.name),
                  'form-success')
            return redirect(url_for('descriptor.new_descriptor'))
    return render_template('descriptor/new_descriptor.html', form=form)


@descriptor.route('/<int:desc_id>', methods=['GET', 'POST'])
@login_required
def descriptor_info(desc_id):
    """Display the descriptor info."""
    descriptor = Descriptor.query.get(desc_id)
    is_option = len(descriptor.values) != 0
    if descriptor is None:
        abort(404)
    return render_template('descriptor/manage_descriptor.html',
                           desc=descriptor, is_option=is_option)


@descriptor.route('/<int:desc_id>/name', methods=['GET', 'POST'])
@login_required
def edit_name(desc_id):
    """Edit a descriptor's name."""
    descriptor = Descriptor.query.get(desc_id)
    is_option = len(descriptor.values) != 0
    old_name = descriptor.name
    if descriptor is None:
        abort(404)
    form = EditDescriptorNameForm()
    if form.validate_on_submit():
        descriptor.name = form.name.data
        db.session.add(descriptor)
        db.session.commit()
        flash('Name for descriptor {} successfully changed to {}.'
              .format(old_name, descriptor.name),
              'form-success')
        return render_template('descriptor/manage_descriptor.html',
                               desc=descriptor, is_option=is_option)
    form.name.data = descriptor.name
    return render_template('descriptor/manage_descriptor.html',
                           desc=descriptor, form=form, is_option=is_option)


@descriptor.route('/<int:desc_id>/option-values')
@login_required
def change_option_values_request(desc_id):
    """Shows the page for changing descriptor's option values."""
    descriptor = Descriptor.query.get(desc_id)
    is_option = len(descriptor.values) != 0
    if not is_option:
        abort(404)
    return render_template('descriptor/manage_descriptor.html',
                           desc=descriptor, is_option=is_option,
                           desc_id=desc_id)


@descriptor.route('/<int:desc_id>/option-values/edit/<int:option_index>',
                  methods=['GET', 'POST'])
@login_required
def edit_option_value(desc_id, option_index):
    """Edt a descriptor's option values."""
    descriptor = Descriptor.query.get(desc_id)
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
        db.session.commit()  # Currently not working.
        flash('Value {} for descriptor {} successfully changed to {}.'
              .format(old_value, descriptor.name,
                      descriptor.values[option_index]),
              'form-success')
    else:
        form.value.data = descriptor.values[option_index]
    return render_template('descriptor/manage_descriptor.html',
                           desc=descriptor, is_option=is_option,
                           desc_id=desc_id, form=form)


@descriptor.route('/<int:desc_id>/option_values/remove/<int:option_index>',
                  methods=['GET', 'POST'])
@login_required
def remove_option_value(desc_id, option_index):
    """Remove a descriptor's option values."""

    descriptor = Descriptor.query.get(desc_id)

    option_assocs = OptionAssociation.query.filter(db.and_(
        OptionAssociation.descriptor_id == desc_id,
        OptionAssociation.option == option_index
        )).all()

    form = FixAllResourceOptionValueForm()

    values = ['Remove this descriptor'] + descriptor.values[:option_index] + \
        descriptor.values[option_index + 1:]
    values_with_labels = map(lambda x: (x, x), values)
    for i in range(len(option_assocs)):
        form.resources.append_entry()
        form.resources.entries[i].option.choices = values_with_labels
        form.resources.entries[i].resource_id = option_assocs[i].resource_id

    if form.validate_on_submit():
        values_to_index = {}
        for i in range(len(values)):
            values_to_index[values[i]] = i - 1
        for resource in form.resources.data:
            if values_to_index[resource.option.data] == -1:
                OptionAssociation.delete().where(
                    OptionAssociation.resource_id == resource.resource_id
                    )
            else:
                OptionAssociation.update().where(
                    OptionAssociation.resource_id == resource.resource_id
                    ).values(
                        option=values_to_index[resource.option.data]
                    )
        db.session.commit()
        flash('Value {} for descriptor {} successfully removed.'
              .format(descriptor.values[option_index], descriptor.name),
              'form-success')
        return redirect(url_for('descriptor.info', desc_id=desc_id))

    return render_template('descriptor/confirm_resources.html',
                           option_assocs=option_assocs, desc_id=desc_id,
                           desc=descriptor, option_index=option_index,
                           form=form)


@descriptor.route('/<int:desc_id>/delete')
@login_required
def delete_descriptor_request(desc_id):
    """Request deletion of a user's account."""
    descriptor = Descriptor.query.get(desc_id)
    is_option = len(descriptor.values) != 0
    if descriptor is None:
        abort(404)
    return render_template('descriptor/manage_descriptor.html',
                           desc=descriptor, is_option=is_option)


@descriptor.route('/<int:desc_id>/delete')
@login_required
def delete_descriptor(desc_id):
    """Deletes a descriptor."""
    descriptor = Descriptor.query.get(desc_id)
    db.session.delete(descriptor)
    db.session.commit()
    flash('Successfully deleted descriptor %s.' % descriptor.name, 'success')
    return redirect(url_for('descriptor.index'))
