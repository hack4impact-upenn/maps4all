from flask import flash, redirect, render_template, url_for
from flask.ext.login import login_required
from sqlalchemy.exc import IntegrityError
from wtforms.fields import SelectField, StringField, SubmitField

from .. import db
from ..models import Descriptor, OptionAssociation, Resource, TextAssociation
from . import single_resource
from .forms import BaseForm, SingleResourceForm


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
    form = SingleResourceForm()
    if form.validate_on_submit():
        new_resource = Resource(name=form.name.data,
                                address=form.address.data,
                                latitude=form.latitude.data,
                                longitude=form.longitude.data)
        db.session.add(new_resource)
        try:
            db.session.commit()
            flash('Resource added', 'form-success')
            new_resource_id = Resource.query.order_by('-id').first().id
            return redirect(url_for('single_resource.edit',
                                    resource_id=new_resource_id))
        except IntegrityError:
            db.session.rollback()
            flash('Error: failed to save resource. Please try again.',
                  'form-error')
    return render_template('single_resource/create.html', form=form)


@single_resource.route('/<int:resource_id>', methods=['GET', 'POST'])
@login_required
def edit(resource_id):
    """Edit a resource."""
    # Handling and rendering the form for editing the main resource data
    resource = Resource.query.get(resource_id)
    field_names = Resource.__table__.columns.keys()
    resource_main_form = SingleResourceForm()
    if resource_main_form.validate_on_submit():
        resource.name = resource_main_form.name.data
        resource.address = resource_main_form.address.data
        resource.latitude = resource_main_form.latitude.data
        resource.longitude = resource_main_form.longitude.data
        try:
            db.session.commit()
            flash('Resource updated', 'form-success')
            return redirect(url_for('single_resource.edit',
                                    resource_id=resource_id))
        except IntegrityError:
            db.session.rollback()
            flash('Error: failed to save resource. Please try again.',
                  'form-error')
    for field_name in field_names[1:]:
        resource_main_form[field_name].data = resource.__dict__[field_name]
    # Handling and rendering the form for editing the resource descriptors
    descriptors = Descriptor.query.all()
    for descriptor in descriptors:
        if (descriptor.values):
            choices = [(v, v) for v in descriptor.values]
            default = None
            association = OptionAssociation.query.filter_by(
                resource_id=resource_id,
                descriptor_id=descriptor.id
            ).first()
            if (association is not None):
                default = descriptor.values[association.option]
            setattr(
                BaseForm,
                descriptor.name,
                SelectField(choices=choices, default=default)
            )
        else:
            default = None
            association = TextAssociation.query.filter_by(
                resource_id=resource_id,
                descriptor_id=descriptor.id
            ).first()
            if (association is not None):
                default = association.text
            setattr(BaseForm, descriptor.name, StringField(default=default))
    setattr(BaseForm, 'submit', SubmitField('Save Data'))
    resource_descriptors_form = BaseForm()
    return render_template('single_resource/edit.html',
                           resource_id=resource_id,
                           form=resource_main_form,
                           resource_descriptors_form=resource_descriptors_form)
