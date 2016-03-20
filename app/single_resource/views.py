from flask import flash, redirect, render_template, url_for
from flask.ext.login import login_required
from sqlalchemy.exc import IntegrityError

from .. import db
from ..models import Resource
from . import single_resource
from .forms import CreateResourceForm


@single_resource.route('/')
@login_required
def index():
    field_names = Resource.__table__.columns.keys()[1:]  # excluding 'id'
    resources = Resource.query.all()
    return render_template('single_resource/index.html',
                           field_names=field_names,
                           resources=resources)


@single_resource.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    form = CreateResourceForm()
    if form.validate_on_submit():
        new_resource = Resource(name=form.name.data,
                                address=form.address.data,
                                latitude=form.latitude.data,
                                longitude=form.longitude.data)
        db.session.add(new_resource)
        try:
            db.session.commit()
            flash('Resource added', 'form-success')
            return redirect(url_for('single_resource.create'))
        except IntegrityError:
            db.session.rollback()
            flash('Error: failed to save resource. Please try again.',
                  'form-error')
    return render_template('single_resource/create.html', form=form)
