from flask import abort, flash, render_template, redirect, url_for
from flask.ext.login import login_required

from forms import (
    ChangeNameForm,
    EditResourceOptionForm,
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
        db.session.add(descriptor)
        db.session.commit()
        flash('Descriptor {} successfully created'.format(descriptor.name),
              'form-success')
        return redirect(url_for('descriptor.new_descriptor'))
    return render_template('descriptor/new_descriptor.html', form=form)


@descriptor.route('/<int:desc_id>', methods=['GET', 'POST'])
@descriptor.route('/<int:desc_id>/info')
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
def change_name(desc_id):
    """Change a descriptor's name."""
    descriptor = Descriptor.query.get(desc_id)
    old_name = descriptor.name
    if descriptor is None:
        abort(404)
    form = ChangeNameForm()
    if form.validate_on_submit():
        descriptor.name = form.name.data
        db.session.add(descriptor)
        db.session.commit()
        flash('Name for descriptor {} successfully changed to {}.'
              .format(old_name, descriptor.name),
              'form-success')
    else:
        form.name.data = descriptor.name
    return render_template('descriptor/manage_descriptor.html',
                           desc=descriptor, form=form)


@descriptor.route('/<int:desc_id>/option-values')
@login_required
def change_option_values_request(desc_id):
    """Request change of a descriptor's option values."""
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
    """Request change of a descriptor's option values."""
    descriptor = Descriptor.query.get(desc_id)
    is_option = len(descriptor.values) != 0
    form = EditResourceOptionForm()
    if not is_option:
        abort(404)
    if form.validate_on_submit():
        old_value = descriptor.values[option_index]
        descriptor.values[option_index] = form.value.data
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


@descriptor.route('/<int:desc_id>/option_values/remove/<int:option_index>')
@login_required
def remove_option_value(desc_id, option_index):
    """Remove a descriptor's option values."""

    descriptor = Descriptor.query.get(desc_id)

    option_assocs = OptionAssociation.query.filter(db.and_(
        OptionAssociation.descriptor_id == desc_id,
        OptionAssociation.option == option_index
        )).all()

    # TODO: Make this into some sort of form to modify the resources

    return render_template('descriptor/confirm_resources.html',
                           option_assocs=option_assocs, desc_id=desc_id,
                           desc=descriptor, option_index=option_index)


@descriptor.route('/<int:desc_id>/delete')
@login_required
def delete_descriptor_request(desc_id):
    """Request deletion of a user's account."""
    descriptor = Descriptor.query.get(desc_id)
    if descriptor is None:
        abort(404)
    return render_template('descriptor/manage_descriptor.html',
                           desc=descriptor)


@descriptor.route('/<int:desc_id>/delete')
@login_required
def delete_descriptor(desc_id):
    """Deletes a descriptor."""
    descriptor = Descriptor.query.get(desc_id)
    db.session.delete(descriptor)
    db.session.commit()
    flash('Successfully deleted descriptor %s.' % descriptor.name, 'success')
    return redirect(url_for('descriptor.index'))
