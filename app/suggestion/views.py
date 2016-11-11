import pytz

from datetime import datetime
from flask import abort, flash, redirect, render_template, url_for
from flask.ext.login import login_required
from sqlalchemy.exc import IntegrityError

from . import suggestion
from .. import db
from ..models import Resource, Suggestion, Descriptor
from forms import SuggestionContactForm, SuggestionBasicForm, SuggestionAdvancedForm
from wtforms.fields import TextAreaField, SelectField


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
    contact_form = SuggestionContactForm()
    basic_form = SuggestionBasicForm()
    if resource_id is None:
        name = None
        resource = None
    else:
        resource = Resource.query.get(resource_id)
        if resource is None:
            abort(404)
        name = resource.name
    descriptors = Descriptor.query.all()
    for descriptor in descriptors:
        if descriptor.values:
            choices = [(str(i), v) for i, v in enumerate(descriptor.values)]
            setattr(SuggestionAdvancedForm,
                    descriptor.name,
                    SelectField(choices=choices))
        else:
            setattr(SuggestionAdvancedForm, descriptor.name, TextAreaField())
    advanced_form = SuggestionAdvancedForm()
    # if form.validate_on_submit():
    #     suggestion = Suggestion(
    #         resource_id=resource_id,
    #         suggestion_text=form.suggestion_text.data,
    #         contact_name=form.contact_name.data,
    #         contact_email=form.contact_email.data,
    #         contact_phone_number=form.contact_phone_number.data,
    #         submission_time=datetime.now(pytz.timezone('US/Eastern'))
    #     )
    #     db.session.add(suggestion)
    #     try:
    #         db.session.commit()
    #         flash('Thanks for the suggestion!', 'success')
    #         return redirect(url_for('main.index'))
    #     except IntegrityError:
    #         db.session.rollback()
    #         flash('Database error occurred. Please try again.', 'error')
    return render_template('suggestion/suggest.html', contact_form=contact_form, name=name, basic_form=basic_form,
                            advanced_form=advanced_form)
