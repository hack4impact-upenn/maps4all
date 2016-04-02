from flask import abort, flash, render_template, redirect, url_for
from flask.ext.login import login_required

from forms import ChangeNameForm, EditDescriptorForm, NewDescriptorForm
from . import descriptor
from .. import db
from ..models import Descriptor


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
    descriptor = Descriptor.query.filter_by(id=desc_id).first()
    if descriptor is None:
        abort(404)
    return render_template('descriptor/manage_descriptor.html',
                           desc=descriptor)


@descriptor.route('/<int:desc_id>/change-name', methods=['GET', 'POST'])
@login_required
def change_name(desc_id):
    """Change a descriptor's name."""
    descriptor = Descriptor.query.filter_by(id=desc_id).first()
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


@descriptor.route('/<int:desc_id>/change-option-values',
                  methods=['GET', 'POST'])
@login_required
def change_option_values(desc_id):
    """Change a descriptor's option values."""
    descriptor = Descriptor.query.filter_by(id=desc_id).first()
    if descriptor is None:
        abort(404)
    form = ChangeNameForm()
    if form.validate_on_submit():
        descriptor.name = form.name.data
        db.session.add(descriptor)
        db.session.commit()
        flash('Option for descriptor {} successfully changed.'
              .format(descriptor.name),
              'form-success')
    return render_template('descriptor/manage_descriptor.html',
                           desc=descriptor,
                           form=form)


@descriptor.route('/<int:desc_id>/delete')
@login_required
def delete_descriptor_request(desc_id):
    """Request deletion of a user's account."""
    descriptor = Descriptor.query.filter_by(id=desc_id).first()
    if descriptor is None:
        abort(404)
    return render_template('descriptor/manage_descriptor.html',
                           desc=descriptor)


@login_required
def edit_descriptor(desc_id):
    """Edit a new descriptor."""
    form = EditDescriptorForm()
    descriptor = Descriptor.query.filter_by(id=desc_id).first()
    is_option = len(descriptor.values) != 0

    if form.validate_on_submit():
        values = []
        for v in form.option_values.data:
            if v is not None and len(v) != 0:
                values.append(v)
        descriptor.name = form.name.data
        descriptor.values = values
        db.session.add(descriptor)
        db.session.commit()
        flash('Successfully editted descriptor %s.' % descriptor.name,
              'success')
        return redirect(url_for('descriptor.index'))
    else:
        form.name.data = descriptor.name
        for i in range(10):
            if i < len(descriptor.values):
                form.option_values.append_entry(descriptor.values[i])
            else:
                form.option_values.append_entry()
    return render_template('descriptor/edit_descriptor.html', form=form,
                           is_option=is_option, desc_id=desc_id)


@descriptor.route('/<int:desc_id>/delete')
@login_required
def delete_descriptor(desc_id):
    """Deletes a descriptor."""
    descriptor = Descriptor.query.filter_by(id=desc_id).first()
    db.session.delete(descriptor)
    db.session.commit()
    flash('Successfully deleted descriptor %s.' % descriptor.name, 'success')
    return redirect(url_for('descriptor.index'))
