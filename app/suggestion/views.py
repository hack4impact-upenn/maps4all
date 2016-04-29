from datetime import datetime
from flask import abort, flash, render_template, redirect, url_for
from flask.ext.login import login_required
import pytz
from sqlalchemy.exc import IntegrityError
from . import suggestion
from .. import db
from ..models import Resource, Suggestion

from forms import SuggestionForm


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
    print num_unread
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


@suggestion.route('/create',  methods=['GET', 'POST'])
def create():
    """Create a suggestion for a new resource."""
    form = SuggestionForm()
    if form.validate_on_submit():
        suggestion = Suggestion(
            suggestion_text=form.suggestion_text.data,
            contact_name=form.contact_name.data,
            contact_email=form.contact_email.data,
            contact_phone_number=form.contact_phone_number.data,
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
    return render_template('suggestion/suggest.html', form=form,
                           existing=False)


@suggestion.route('/edit/<int:resource_id>',  methods=['GET', 'POST'])
def edit(resource_id):
    """Create a suggestion for an existing resource."""
    form = SuggestionForm()
    resource = Resource.query.get(resource_id)
    if resource is None:
        abort(404)
    if form.validate_on_submit():
        suggestion = Suggestion(
            resource_id=resource_id,
            suggestion_text=form.suggestion_text.data,
            contact_name=form.contact_name.data,
            contact_email=form.contact_email.data,
            contact_phone_number=form.contact_phone_number.data,
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
    return render_template('suggestion/suggest.html', form=form,
                           existing=True, name=resource.name)
