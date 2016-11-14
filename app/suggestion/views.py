import pytz

from datetime import datetime
from flask import abort, flash, redirect, render_template, url_for
from flask.ext.login import login_required
from sqlalchemy.exc import IntegrityError

from . import suggestion
from .. import db
from ..models import Resource, Suggestion, Descriptor
from forms import SuggestionBasicForm, SuggestionAdvancedForm
from wtforms.fields import TextAreaField, SelectField
from ..single_resource.views import save_associations
from ..single_resource.forms import SingleResourceForm


@suggestion.route('/')
@login_required
def index():
    """View all suggestions in a list."""
    suggestions = Suggestion.query.all()
    return render_template('suggestion/index.html', suggestions=suggestions)


@suggestion.route('/unread')
@login_required
def unread():
    """Returns the number of unread suggestions."""
    num_unread = Suggestion.query.filter(
        Suggestion.read == False  # noqa
        ).count()
    return "%d" % num_unread


@suggestion.route('/toggle-read/<int:sugg_id>')
@login_required
def toggle_read(sugg_id):
    """Toggles the readability of a given suggestion."""
    suggestion = Suggestion.query.get(sugg_id)
    if suggestion is None:
        abort(404)
    suggestion.read = not suggestion.read
    db.session.add(suggestion)
    try:
        db.session.commit()
    except:
        db.session.rollback()
        flash('Database error occurred. Please try again.', 'error')
    return redirect(url_for('suggestion.index'))


@suggestion.route('/delete/<int:sugg_id>')
@login_required
def delete(sugg_id):
    """Delete a given suggestion."""
    suggestion = Suggestion.query.get(sugg_id)
    if suggestion is None:
        abort(404)
    db.session.delete(suggestion)
    try:
        db.session.commit()
        flash('Suggestion successfully deleted.', 'success')
    except:
        db.session.rollback()
        flash('Database error occurred. Please try again.', 'error')
    return redirect(url_for('suggestion.index'))


@suggestion.route('/new', defaults={'resource_id': None},
                  methods=['GET', 'POST'])
@suggestion.route('/<int:resource_id>',  methods=['GET', 'POST'])
def suggest(resource_id):
    """Create a suggestion for a resource."""
    basic_form = SuggestionBasicForm()
    if resource_id is None:
        name = None
        resource = None
    else:
        resource = Resource.query.get(resource_id)
        if resource is None:
            abort(404)
        name = resource.name
    advanced_form = SuggestionAdvancedForm()
    create_descriptor_form(advanced_form)
    if basic_form.validate_on_submit():
        suggestion = Suggestion(
            resource_id=resource_id,
            suggestion_text=basic_form.suggestion_text.data,
            contact_name=basic_form.contact_name.data,
            contact_email=basic_form.contact_email.data,
            contact_phone_number=basic_form.contact_phone_number.data,
            resource_name=basic_form.name.data,
            resource_address=basic_form.address.data,
            submission_time=datetime.now(pytz.timezone('US/Eastern'))
        )
        db.session.add(suggestion)
        try:
            db.session.commit()
            flash('Thanks for the suggestion!', 'success')
            return redirect(url_for('main.index'))
        except IntegrityError:
            db.session.rollback()
            flash('Database error occurred. Please try again.', 'error')
    return render_template('suggestion/suggest.html', name=name, basic_form=basic_form,
                            advanced_form=advanced_form)


@suggestion.route('/create/<int:sugg_id>', methods=['GET', 'POST'])
@login_required
def create(sugg_id):
    suggestion = Suggestion.query.get(sugg_id)
    if suggestion is None:
        abort(404)
    descriptors = Descriptor.query.all()
    for descriptor in descriptors:
        if descriptor.values:  # Fields for option descriptors.
            choices = [(str(i), v) for i, v in enumerate(descriptor.values)]
            setattr(SingleResourceForm,
                    descriptor.name,
                    SelectField(choices=choices))
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
            return redirect(url_for('suggestion.index'))
        except IntegrityError:
            db.session.rollback()
            flash('Error: failed to save resource. Please try again.',
                  'form-error')
    return render_template('suggestion/create.html', form=form, suggestion=suggestion)