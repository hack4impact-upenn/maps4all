from flask import flash, redirect, render_template, url_for
from flask.ext.login import login_required
from sqlalchemy.exc import IntegrityError

from .. import db
from ..models import Resource
from . import single_resource
from .forms import SingleResourceForm


@single_resource.route('/')
@login_required
def index():
    """View resources in a list."""
    field_names = Resource.__table__.columns.keys()
    resources = Resource.query.all()
    return render_template('single_resource/index.html',
                           field_names=field_names,
                           resources=resources)


@single_resource.route('/create', methods=('GET', 'POST'))
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


@single_resource.route('/<int:resource_id>', methods=('GET', 'POST'))
@login_required
def edit(resource_id):
    """Edit a resource."""
    resource = Resource.query.get(resource_id)
    field_names = Resource.__table__.columns.keys()
    form = SingleResourceForm()
    if form.validate_on_submit():
        resource.name = form.name.data
        resource.address = form.address.data
        resource.latitude = form.latitude.data
        resource.longitude = form.longitude.data
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
        form[field_name].data = resource.__dict__[field_name]
    return render_template('single_resource/edit.html',
                           form=form,
                           resource_id=resource_id)
