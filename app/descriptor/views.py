from flask import render_template, redirect, flash, url_for
from flask.ext.login import login_required

from forms import EditDescriptorForm, NewDescriptorForm
from . import descriptor
from .. import db
from ..models import Descriptor


@descriptor.route('/')
@login_required
def index():
    return render_template('descriptor/index.html')


@descriptor.route('/descriptors')
@login_required
def existing_descriptors():
    """View all resource descriptors."""
    descriptors = Descriptor.query.all()
    return render_template('descriptor/descriptors.html',
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


@descriptor.route('/descriptor/<int:desc_id>', methods=['GET', 'POST'])
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
        return redirect(url_for('descriptor.existing_descriptors'))
    else:
        form.name.data = descriptor.name
        for i in range(10):
            if i < len(descriptor.values):
                form.option_values.append_entry(descriptor.values[i])
            else:
                form.option_values.append_entry()
    return render_template('descriptor/edit_descriptor.html', form=form,
                           is_option=is_option, desc_id=desc_id)


@descriptor.route('/descriptor/<int:desc_id>/delete')
@login_required
def delete_descriptor(desc_id):
    """Deletes a descriptor."""
    descriptor = Descriptor.query.filter_by(id=desc_id).first()
    db.session.delete(descriptor)
    db.session.commit()
    flash('Successfully deleted descriptor %s.' % descriptor.name, 'success')
    return redirect(url_for('descriptor.existing_descriptors'))
