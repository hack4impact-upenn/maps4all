import os
import datetime
from flask import abort, flash, redirect, render_template, url_for, current_app
from flask.ext.login import current_user, login_required
from flask.ext.rq import get_queue
from werkzeug.utils import secure_filename

from . import admin
from .. import db
<<<<<<< HEAD
from ..models import Role, User, Rating, Resource, EditableHTML
from forms import (
=======
from ..models import Role, User, Rating, Resource, SiteAttribute
from .forms import (
>>>>>>> 1e756054e28d65bd999d4ea3ff73031f28e8262d
    ChangeAccountTypeForm,
    ChangeUserEmailForm,
    InviteUserForm,
    NewUserForm,
<<<<<<< HEAD
    NewPageForm
=======
    ChangeSiteNameForm,
    ChangeSiteLogoForm,
    ChangeSiteStyleForm
>>>>>>> 1e756054e28d65bd999d4ea3ff73031f28e8262d
)
from ..email import send_email


@admin.route('/')
@login_required
def index():
    """Admin dashboard page."""
    return render_template('admin/index.html')


@admin.route('/new-user', methods=['GET', 'POST'])
@login_required
def new_user():
    """Create a new user."""
    form = NewUserForm()
    if form.validate_on_submit():
        user = User(role=form.role.data,
                    first_name=form.first_name.data,
                    last_name=form.last_name.data,
                    email=form.email.data,
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('User {} successfully created'.format(user.full_name()),
              'form-success')
    return render_template('admin/new_user.html', form=form)

@admin.route('/invite-user', methods=['GET', 'POST'])
@login_required
def invite_user():
    """Invites a new user to create an account and set their own password."""
    form = InviteUserForm()
    if form.validate_on_submit():
        user = User(role=form.role.data,
                    first_name=form.first_name.data,
                    last_name=form.last_name.data,
                    email=form.email.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        invite_link = url_for('account.join_from_invite', user_id=user.id,
                              token=token, _external=True)
        get_queue().enqueue(
            send_email,
            recipient=user.email,
            subject='You Are Invited To Join',
            template='account/email/invite',
            user=user,
            invite_link=invite_link,
        )
        flash('User {} successfully invited'.format(user.full_name()),
              'form-success')
    return render_template('admin/new_user.html', form=form)


@admin.route('/users')
@login_required
def registered_users():
    """View all registered users."""
    users = User.query.all()
    roles = Role.query.all()
    return render_template('admin/registered_users.html', users=users,
                           roles=roles)


@admin.route('/user/<int:user_id>')
@admin.route('/user/<int:user_id>/info')
@login_required
def user_info(user_id):
    """View a user's profile."""
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        abort(404)
    return render_template('admin/manage_user.html', user=user)


@admin.route('/user/<int:user_id>/change-email', methods=['GET', 'POST'])
@login_required
def change_user_email(user_id):
    """Change a user's email."""
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        abort(404)
    form = ChangeUserEmailForm()
    if form.validate_on_submit():
        user.email = form.email.data
        db.session.add(user)
        db.session.commit()
        flash('Email for user {} successfully changed to {}.'
              .format(user.full_name(), user.email),
              'form-success')
    return render_template('admin/manage_user.html', user=user, form=form)


@admin.route('/user/<int:user_id>/change-account-type',
             methods=['GET', 'POST'])
@login_required
def change_account_type(user_id):
    """Change a user's account type."""
    if current_user.id == user_id:
        flash('You cannot change the type of your own account. Please ask '
              'another administrator to do this.', 'error')
        return redirect(url_for('admin.user_info', user_id=user_id))

    user = User.query.get(user_id)
    if user is None:
        abort(404)
    form = ChangeAccountTypeForm()
    if form.validate_on_submit():
        user.role = form.role.data
        db.session.add(user)
        db.session.commit()
        flash('Role for user {} successfully changed to {}.'
              .format(user.full_name(), user.role.name),
              'form-success')
    return render_template('admin/manage_user.html', user=user, form=form)


@admin.route('/user/<int:user_id>/delete')
@login_required
def delete_user_request(user_id):
    """Request deletion of a user's account."""
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        abort(404)
    return render_template('admin/manage_user.html', user=user)


@admin.route('/user/<int:user_id>/_delete')
@login_required
def delete_user(user_id):
    """Delete a user's account."""
    if current_user.id == user_id:
        flash('You cannot delete your own account. Please ask another '
              'administrator to do this.', 'error')
    else:
        user = User.query.filter_by(id=user_id).first()
        db.session.delete(user)
        db.session.commit()
        flash('Successfully deleted user %s.' % user.full_name(), 'success')
    return redirect(url_for('admin.registered_users'))

@admin.route('/ratings-table')
@login_required
def ratings_table():
    """Ratings and Reviews Table."""
    ratings = Rating.query.all()
    for rating in ratings:
        if rating.resource_id is not None:
            temp = Resource.query.filter_by(id=rating.resource_id)
            if temp is not None:
                rating.resource_name = temp.first().name
    return render_template('rating/index.html', ratings=ratings)

@admin.route('/create-static-page', methods=['GET', 'POST'])
@login_required
def create_page():
    form = NewPageForm()
    if form.validate_on_submit():
        if( not EditableHTML.get_editable_html(form.editor_name.data)):
            editor_name = form.editor_name.data
            editor_name = editor_name.lower().strip()
            editable_html_obj = EditableHTML(editor_name=editor_name, page_name=form.page_name.data, value=' ')
            db.session.add(editable_html_obj)
            db.session.commit()
        else: 
            flash('There is already a static page at that URL', 'error')
    return render_template('/admin/create_pages.html', form=form)

@admin.route('/customize-site')
@login_required
def customize_site():
    """Customize the site"""
    return render_template('admin/customize_site.html',
                           app_name=SiteAttribute.get_value("ORG_NAME"))


@admin.route('/customize-site/name', methods=['GET', 'POST'])
@login_required
def change_site_name():
    """Change a site's name."""
    site_name = SiteAttribute.get("ORG_NAME")

    form = ChangeSiteNameForm()
    if form.validate_on_submit():
        site_name.value = form.site_name.data
        db.session.add(site_name)
        db.session.commit()
        flash('Site name successfully changed to {}.'
              .format(form.site_name.data),
              'form-success')
    return render_template('admin/customize_site.html',
                           app_name=site_name.value, form=form)


@admin.route('/customize-site/logo', methods=['GET', 'POST'])
@login_required
def change_site_logo():
    """Change a site's logo."""
    logo_url = SiteAttribute.get("SITE_LOGO")

    form = ChangeSiteLogoForm()
    if form.validate_on_submit():
        site_logo = form.site_logo.data
        filename = secure_filename(site_logo.filename)

        site_logo.save(os.path.join(
            current_app.root_path, 'static/custom', filename
        ))

        logo_url.value = str(filename)
        db.session.add(logo_url)
        db.session.commit()

        flash('Site logo successfully changed to <br>' +
              '<img width="70px" src="{}"/>'
              .format(url_for('static', filename='custom/' + logo_url.value)),
              'form-success')

    return render_template('admin/customize_site.html',
                           app_name=SiteAttribute.get_value("ORG_NAME"),
                           form=form)


@admin.route('/customize-site/style', methods=['GET', 'POST'])
@login_required
def change_site_style():
    """Change a site's stylesheet."""
    style_sheet = SiteAttribute.get("STYLE_SHEET")
    style_time = SiteAttribute.get("STYLE_TIME")

    form = ChangeSiteStyleForm()
    if form.validate_on_submit():
        site_style = form.site_style.data
        filename = 'style.css'

        site_style.save(os.path.join(
            current_app.root_path, 'static/custom', filename
        ))

        style_sheet.value = str(filename)
        db.session.add(style_sheet)
        style_time.value = str(datetime.datetime.utcnow()).replace(' ', '-')
        db.session.add(style_time)
        db.session.commit()

        flash('Site style successfully changed.', 'form-success')

    return render_template('admin/customize_site.html',
                           app_name=SiteAttribute.get_value("ORG_NAME"),
                           form=form)
