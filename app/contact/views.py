from flask import render_template, redirect, url_for, abort, flash
from flask.ext.login import login_required
from flask.ext.rq import get_queue

from wtforms.fields import SelectField

from .. import db
from ..models import EditableHTML, Resource, ContactCategory
from . import contact
from forms import ContactForm, ContactCategoryForm, EditCategoryNameForm
from ..email import send_email

@contact.route('/', methods=['GET', 'POST'])
def index():
    editable_html_obj = EditableHTML.get_editable_html('contact')
    setattr(ContactForm,
            'category',
            SelectField('Category', choices=[(c.name, c.name) for c in ContactCategory.query.all()]))
    form = ContactForm()
    contact_email = 'maps4all.team@gmail.com'
    if form.validate_on_submit():
        get_queue().enqueue(
            send_email,
            recipient=contact_email,
            subject=form.category.data,
            template='contact/email/contact',
            name=form.name.data,
            email=form.email.data,
            message=form.message.data
        )
        return redirect(url_for('main.index'))
    category_form = ContactCategoryForm()
    if category_form.validate_on_submit():
        new_category = ContactCategory(name=category_form.name.data)
        db.session.add(new_category)
        db.session.commit()
    categories = ContactCategory.query.all()
    return render_template('contact/index.html',
                           editable_html_obj=editable_html_obj,
                           form=form,
                           category_form=category_form,
                           categories=categories)

@contact.route('/<int:category_id>', methods=['GET', 'POST'])
@login_required
def edit_category_name(category_id):
    """Edit a category"""
    category = ContactCategory.query.get(category_id)
    if category is None:
        abort(404)
    old_name = category.name
    form = EditCategoryNameForm()
    if form.validate_on_submit():
        if ContactCategory.query.filter(ContactCategory.name == form.name.data).first() is not None:
            flash('Category {} already exists.'.format(form.name.data), 'form-error')
            return render_template(
                                'contact/manage_category.html',
                                category=category,
                                form=form)
        category.name = form.name.data
        db.session.add(category)
        try:
            db.session.commit()
            flash('Name for category {} successfully changed to {},'
                .format(old_name, category.name),
                'form-success')
        except IntegrityError:
            db.session.rollback()
            flash('Database error occurred. Please try again', 'form-error')
        return render_template(
                            'contact/manage_category.html',
                            category=category,
                            form=form)
    form.name.data = category.name
    return render_template(
                        'contact/manage_category.html',
                        category=category,
                        form=form)

@contact.route('/<int:category_id>/delete_request')
@login_required
def delete_category_request(category_id):
    """Shows the page for deletion of a contact category."""
    category = ContactCategory.query.get(category_id)
    if category is None:
        abort(404)
    return render_template(
                        'contact/manage_category.html',
                        category=category)

@contact.route('/<int:category_id>/delete')
@login_required
def delete_category(category_id):
    """Deletes a contact category."""
    category = ContactCategory.query.get(category_id)
    if category is None:
        abort(404)
    db.session.delete(category)
    try:
        db.session.commit()
        flash('Successfully deleted category %s.' % category.name, 'success')
    except IntegrityError:
        db.session.rollback()
        flash('Database error occurred. Please try again.', 'form-error')
        return render_template(
                            'contact/manage_category.html',
                            category=category)
    return redirect(url_for('contact.index'))
