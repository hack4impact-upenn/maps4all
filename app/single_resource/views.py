from flask import flash, redirect, render_template, url_for
from flask.ext.login import login_required
from sqlalchemy.exc import IntegrityError
from wtforms.fields import SelectField, StringField

from .. import db
from ..models import Descriptor, OptionAssociation, Resource, TextAssociation
from . import single_resource
from .forms import SingleResourceForm


@single_resource.route('/')
@login_required
def index():
    """View resources in a list."""
    resources = Resource.query.all()
    return render_template('single_resource/index.html', resources=resources)


@single_resource.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Add a resource."""
    descriptors = Descriptor.query.all()
    for descriptor in descriptors:
        if (descriptor.values):  # fields for option descriptors
            choices = [(str(i), v) for i, v in enumerate(descriptor.values)]
            setattr(SingleResourceForm,
                    descriptor.name,
                    SelectField(choices=choices))
        else:  # fields for text descriptors
            setattr(SingleResourceForm, descriptor.name, StringField())
    form = SingleResourceForm()
    if form.validate_on_submit():
        new_resource = Resource(name=form.name.data,
                                address=form.address.data,
                                latitude=form.latitude.data,
                                longitude=form.longitude.data)
        db.session.add(new_resource)
        add_associations(resource=new_resource,
                         form=form,
                         descriptors=descriptors,
                         resource_existed=False)
        try:
            db.session.commit()
            flash('Resource added', 'form-success')
            return redirect(url_for('single_resource.index'))
        except IntegrityError:
            db.session.rollback()
            flash('Error: failed to save resource. Please try again.',
                  'form-error')
    return render_template('single_resource/create.html', form=form)


@single_resource.route('/<int:resource_id>', methods=['GET', 'POST'])
@login_required
def edit(resource_id):
    """Edit a resource."""
    resource = Resource.query.get(resource_id)
    resource_field_names = Resource.__table__.columns.keys()
    descriptors = Descriptor.query.all()
    for descriptor in descriptors:
        if (descriptor.values):  # fields for option descriptors
            choices = [(str(i), v) for i, v in enumerate(descriptor.values)]
            default = None
            option_association = OptionAssociation.query.filter_by(
                resource_id=resource_id,
                descriptor_id=descriptor.id
            ).first()
            if (option_association is not None):
                default = option_association.option
            setattr(SingleResourceForm,
                    descriptor.name,
                    SelectField(choices=choices, default=default))
        else:  # fields for text descriptors
            default = None
            text_association = TextAssociation.query.filter_by(
                resource_id=resource_id,
                descriptor_id=descriptor.id
            ).first()
            if (text_association is not None):
                default = text_association.text
            setattr(SingleResourceForm,
                    descriptor.name,
                    StringField(default=default))
    form = SingleResourceForm()
    if form.validate_on_submit():
        for field_name in resource_field_names[1:]:
            setattr(resource, field_name, form[field_name].data)
        add_associations(resource=resource,
                         form=form,
                         descriptors=descriptors,
                         resource_existed=True)
        try:
            db.session.commit()
            flash('Resource updated', 'form-success')
            return redirect(url_for('single_resource.index'))
        except IntegrityError:
            db.session.rollback()
            flash('Error: failed to save resource. Please try again.',
                  'form-error')
    for field_name in resource_field_names[1:]:
        form[field_name].data = resource.__dict__[field_name]
    return render_template('single_resource/edit.html',
                           resource_id=resource_id,
                           form=form)


def add_associations(resource, form, descriptors, resource_existed=True):
    for descriptor in descriptors:
        if (descriptor.values):
            AssociationClass = OptionAssociation
            value = int(form[descriptor.name].data)
            keyword = 'option'
        else:
            AssociationClass = TextAssociation
            value = form[descriptor.name].data
            keyword = 'text'
        association = None
        if (resource_existed):
            association = AssociationClass.query.filter_by(
                resource_id=resource.id,
                descriptor_id=descriptor.id
            ).first()
        if (association is not None):
            setattr(association, keyword, value)
        else:
            arguments = {'resource_id': resource.id,
                         'descriptor_id': descriptor.id,
                         keyword: value,
                         'resource': resource,
                         'descriptor': descriptor}
            new_association = AssociationClass(**arguments)
            db.session.add(new_association)
