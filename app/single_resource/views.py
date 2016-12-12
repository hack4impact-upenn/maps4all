from flask import abort, flash, redirect, render_template, url_for, request
from flask.ext.login import login_required
from sqlalchemy.exc import IntegrityError
from wtforms.fields import SelectMultipleField, TextAreaField
from wtforms.fields import SelectMultipleField, SelectField, TextAreaField
from flask_wtf.file import InputRequired

from .. import db
from ..models import Descriptor, OptionAssociation, Resource, TextAssociation, RequiredOptionDescriptor
from . import single_resource
from .forms import SingleResourceForm


@single_resource.route('/')
@login_required
def index():
    """View resources in a list."""
    resources = Resource.query.all()
    req_opt_desc = RequiredOptionDescriptor.query.all()[0]
    req_opt_desc = Descriptor.query.filter_by(
        id=req_opt_desc.descriptor_id
    ).first()
    req_options = {}
    if req_opt_desc is not None:
        for val in req_opt_desc.values:
            req_options[val] = False
    return render_template('single_resource/index.html', resources=resources, req_options=req_options)

@single_resource.route('/search')
@login_required
def search_resources():
    name = request.args.get('name')
    if name is None:
        name = ""
    req_options = request.args.getlist('reqoption')
    if req_options is None:
        req_options = []
    resource_pool = Resource.query.filter(Resource.name.contains(name)).all()
    req_opt_desc = RequiredOptionDescriptor.query.all()[0]
    req_opt_desc = Descriptor.query.filter_by(
        id=req_opt_desc.descriptor_id
    ).first()
    resources = list(resource_pool)
    if req_opt_desc is not None and len(req_options) > 0:
        resources = []
        int_req_options = []
        for o in req_options:
            int_req_options.append(req_opt_desc.values.index(str(o)))
        for resource in resource_pool:
            associations = OptionAssociation.query.filter_by(
                resource_id=resource.id,
                descriptor_id=req_opt_desc.id
            )
            for a in associations:
                if a.option in int_req_options:
                    resources.append(resource)
                    break
    query_req_options = {}
    if req_opt_desc is not None:
        for val in req_opt_desc.values:
            query_req_options[val] = val in req_options
    return render_template('single_resource/index.html', resources=resources, query_name=name, req_options=query_req_options)

@single_resource.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Add a resource."""
    descriptors = Descriptor.query.all()
    req_opt_desc = RequiredOptionDescriptor.query.all()[0]
    for descriptor in descriptors:
        if descriptor.values:  # Fields for option descriptors.
            choices = [(str(i), v) for i, v in enumerate(descriptor.values)]
            setattr(SingleResourceForm,
                    descriptor.name,
                    SelectMultipleField(choices=choices))
        else:  # Fields for text descriptors
            setattr(SingleResourceForm, descriptor.name, TextAreaField())
    form = SingleResourceForm()
    if form.validate_on_submit():
        new_resource = Resource(name=form.name.data,
                                address=form.address.data,
                                latitude=form.latitude.data,
                                longitude=form.longitude.data)
        db.session.add(new_resource)
        save_associations(resource=new_resource,
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
    if resource is None:
        abort(404)
    resource_field_names = Resource.__table__.columns.keys()
    descriptors = Descriptor.query.all()
    req_opt_desc = RequiredOptionDescriptor.query.all()[0]
    for descriptor in descriptors:
        if descriptor.values:  # Fields for option descriptors.
            choices = [(str(i), v) for i, v in enumerate(descriptor.values)]
            default = None
            option_associations = OptionAssociation.query.filter_by(
                resource_id=resource_id,
                descriptor_id=descriptor.id
            )
            if option_associations is not None:
                default = [assoc.option for assoc in option_associations]
            setattr(SingleResourceForm,
                    descriptor.name,
                    SelectMultipleField(choices=choices, default=default))
        else:  # Fields for text descriptors.
            default = None
            text_association = TextAssociation.query.filter_by(
                resource_id=resource_id,
                descriptor_id=descriptor.id
            ).first()
            if text_association is not None:
                default = text_association.text
            setattr(SingleResourceForm,
                    descriptor.name,
                    TextAreaField(default=default))
    form = SingleResourceForm()
    if form.validate_on_submit():
        # Field id is not needed for the form, hence omitted with [1:].
        for field_name in resource_field_names[1:]:
            setattr(resource, field_name, form[field_name].data)
        save_associations(resource=resource,
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
    # Field id is not needed for the form, hence omitted with [1:].
    for field_name in resource_field_names[1:]:
        form[field_name].data = resource.__dict__[field_name]
    return render_template('single_resource/edit.html',
                           form=form,
                           resource_id=resource_id)


def save_associations(resource, form, descriptors, resource_existed=True):
    """Save associations from the forms received by 'create' and 'edit' route
    handlers to the database."""
    for descriptor in descriptors:
        if descriptor.values:
            AssociationClass = OptionAssociation
            values = [int(i) for i in form[descriptor.name].data]
            keyword = 'option'
        else:
            AssociationClass = TextAssociation
            values = [form[descriptor.name].data]
            keyword = 'text'
        for value in values:
            association = None
            if resource_existed:
                associations = AssociationClass.query.filter_by(
                    resource_id=resource.id,
                    descriptor_id=descriptor.id
                )
                # for a in associations:
                #     print a
                #     db.session.delete(a)
                #     try:
                #         db.session.commit()
                #         flash('Resource deleted', 'form-success')
                #     except IntegrityError:
                #         db.session.rollback()
                #         flash('Error: failed to delete resource. Please try again.',
                #               'form-error')

            if association is not None:
                ## NEED TO LOOK INTO THIS
                setattr(association, keyword, value)
            else:
                arguments = {'resource_id': resource.id,
                             'descriptor_id': descriptor.id,
                             keyword: value,
                             'resource': resource,
                             'descriptor': descriptor}
                new_association = AssociationClass(**arguments)
                db.session.add(new_association)


@single_resource.route('/<int:resource_id>/delete', methods=['POST'])
@login_required
def delete(resource_id):
    """Delete a resource."""
    resource = Resource.query.get(resource_id)
    db.session.delete(resource)
    try:
        db.session.commit()
        flash('Resource deleted', 'form-success')
        return redirect(url_for('single_resource.index'))
    except IntegrityError:
        db.session.rollback()
        flash('Error: failed to delete resource. Please try again.',
              'form-error')
