import os
import datetime
from flask import (
    abort,
    flash,
    redirect,
    render_template,
    url_for,
    current_app,
    request
)
from flask_login import current_user, login_required
from flask_rq import get_queue
from werkzeug.utils import secure_filename
from sqlalchemy.exc import IntegrityError

from . import admin
from .. import db
from ..decorators import admin_required
from ..models import Role, User, Rating, Resource, EditableHTML, SiteAttribute
from .forms import (
    ChangeAccountTypeForm,
    ChangeUserEmailForm,
    InviteUserForm,
    NewUserForm,
    NewPageForm,
    EditPageForm,
    ChangeSiteNameForm,
    ChangeTwilioCredentialsForm,
    WelcomeModalForm,
    ChangeSiteColorForm
)
from ..email import send_email
from ..utils import s3_upload


@admin.route('/')
@login_required
def index():
    """Admin dashboard page."""
    return render_template('admin/index.html')


@admin.route('/new-user', methods=['GET', 'POST'])
@login_required
@admin_required
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
@admin_required
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
@admin_required
def registered_users():
    """View all registered users."""
    users = User.query.all()
    roles = Role.query.all()
    return render_template('admin/registered_users.html', users=users,
                           roles=roles)


@admin.route('/user/<int:user_id>')
@admin.route('/user/<int:user_id>/info')
@login_required
@admin_required
def user_info(user_id):
    """View a user's profile."""
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        abort(404)
    return render_template('admin/manage_user.html', user=user)


@admin.route('/user/<int:user_id>/change-email', methods=['GET', 'POST'])
@login_required
@admin_required
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
@admin_required
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
@admin_required
def delete_user_request(user_id):
    """Request deletion of a user's account."""
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        abort(404)
    return render_template('admin/manage_user.html', user=user)


@admin.route('/user/<int:user_id>/_delete')
@login_required
@admin_required
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
@admin_required
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
@admin_required
def create_page():
    pages = EditableHTML.query.all()
    form = NewPageForm()
    if form.validate_on_submit():
        if(not EditableHTML.get_editable_html(form.editor_name.data) and not EditableHTML.get_editable_html_by_page_name(form.page_name.data)):
            editable_html_obj = EditableHTML(
                editor_name=form.editor_name.data, page_name=form.page_name.data, value=' ')
            db.session.add(editable_html_obj)
            db.session.commit()
            flash('Successfully added page %s.' % editable_html_obj.page_name, 'form-success')
            pages = EditableHTML.query.all() # update pages in table
        else:
            flash('There is already a page with that URL or page title', 'form-error')
    return render_template('/admin/create_pages.html', form=form, pages=pages)


@admin.route('/manage-pages/<string:editor_name>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_page_name(editor_name):
    """Edit a category"""
    page = EditableHTML.query.filter_by(editor_name=editor_name).first()
    if page is None:
        abort(404)
    form = EditPageForm()
    if form.validate_on_submit():
        page.page_name = form.page_name.data
        db.session.add(page)
        try:
            db.session.commit()
            flash('Page Successfully Changed.'
                  'form-success')
        except IntegrityError:
            db.session.rollback()
            flash('Database error occurred. Please try again.', 'form-error')
        return render_template('admin/manage_pages.html',
                               page=page,
                               form=form)
    form.page_name.data = page.page_name
    return render_template('admin/manage_pages.html',
                           page=page,
                           form=form)


@admin.route('/manage-pages/<string:editor_name>/delete_request')
@login_required
@admin_required
def delete_page_request(editor_name):
    """Shows the page for deletion of a contact category."""
    page = EditableHTML.query.filter_by(editor_name=editor_name).first()
    if page is None:
        abort(404)
    return render_template('admin/manage_pages.html',
                           page=page)


@admin.route('/manage-pages/<string:editor_name>/delete')
@login_required
@admin_required
def delete_page(editor_name):
    """Deletes a contact category."""
    page = EditableHTML.query.filter_by(editor_name=editor_name).first()
    if page is None:
        abort(404)
    db.session.delete(page)
    try:
        db.session.commit()
        flash('Successfully deleted page', 'success')
    except IntegrityError:
        db.session.rollback()
        flash('Database error occurred. Please try again.', 'form-error')
        return render_template('admin/manage_pages.html',
                               page=page)
    return redirect(url_for('admin.index'))


@admin.route('/customize-site')
@login_required
@admin_required
def customize_site():
    """Customize the site"""
    return render_template('admin/customize_site.html',
                           app_name=SiteAttribute.get_value("ORG_NAME"))


@admin.route('/customize-site/name', methods=['GET', 'POST'])
@login_required
@admin_required
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


@admin.route('/customize-site/color', methods=['GET', 'POST'])
@login_required
@admin_required
def change_site_color():
    """Change a site's color."""
    site_color = SiteAttribute.get("SITE_COLOR")

    form = ChangeSiteColorForm()
    if form.validate_on_submit():
        site_color.value = form.site_color.data
        db.session.add(site_color)
        db.session.commit()
        flash('Site color successfully changed',
              'form-success')
    return render_template('admin/customize_site.html',
                           app_name=SiteAttribute.get_value("ORG_NAME"))


@admin.route('/customize-site/logo', methods=['GET', 'POST'])
@login_required
@admin_required
def change_site_logo():
    """Change a site's logo."""
    if request.method == 'POST':
        logo_attr = SiteAttribute.get("SITE_LOGO")

        url = request.form['file_url']
        logo_attr.value = url

        db.session.add(logo_attr)
        db.session.commit()

        flash('Site logo successfully changed.')

        return redirect(url_for('admin.customize_site'))

    return render_template('admin/customize_site.html',
                           app_name=SiteAttribute.get_value("ORG_NAME"))


@admin.route('/customize-site/style', methods=['GET', 'POST'])
@login_required
@admin_required
def change_site_style():
    """Change a site's stylesheet."""
    if request.method == 'POST':
        style_attr = SiteAttribute.get("STYLE_SHEET")

        url = request.form['url']
        style_attr.value = url

        db.session.add(style_attr)
        db.session.commit()

        flash('Site style sheet successfully changed.')

        return redirect(url_for('admin.customize_site'))

    return render_template('admin/customize_site.html',
                           app_name=SiteAttribute.get_value("ORG_NAME"))


@admin.route('/customize-site/twilio', methods=['GET', 'POST'])
@login_required
def change_twilio_credentials():
    """Change the app's Twilio credentials."""
    form = ChangeTwilioCredentialsForm(
        twilio_auth_token=SiteAttribute.get_value("TWILIO_AUTH_TOKEN") or "",
        twilio_account_sid=SiteAttribute.get_value("TWILIO_ACCOUNT_SID") or ""
    )
    if form.validate_on_submit():
        twilio_auth_token = SiteAttribute.get("TWILIO_AUTH_TOKEN")
        twilio_account_sid = SiteAttribute.get("TWILIO_ACCOUNT_SID")
        twilio_auth_token.value = form.twilio_auth_token.data
        twilio_account_sid.value = form.twilio_account_sid.data
        db.session.add(twilio_auth_token)
        db.session.add(twilio_account_sid)
        db.session.commit()
        flash('Twilio credentials successfully updated.', 'form-success')
    return render_template('admin/customize_site.html', app_name=SiteAttribute.get_value("ORG_NAME"), form=form)

@admin.route('/customize-site/welcome', methods=['GET', 'POST'])
@login_required
def change_welcome_message():
    """Customize the app's welcome modal."""
    form = WelcomeModalForm(
        has_welcome_modal=SiteAttribute.get_value('HAS_WELCOME_MODAL') or 'No',
        header=SiteAttribute.get_value('WELCOME_HEADER') or '',
        content=SiteAttribute.get_value('WELCOME_CONTENT') or '',
        action=SiteAttribute.get_value('WELCOME_ACTION') or '',
        footer=SiteAttribute.get_value('WELCOME_FOOTER') or '',
        website_text=SiteAttribute.get_value('WELCOME_WEBSITE_TEXT') or '',
        website_url=SiteAttribute.get_value('WELCOME_WEBSITE_URL') or '',
        email=SiteAttribute.get_value('WELCOME_EMAIL') or '',
        facebook_url=SiteAttribute.get_value('WELCOME_FACEBOOK_URL') or '',
        twitter_url=SiteAttribute.get_value('WELCOME_TWITTER_URL') or '',
        instagram_url=SiteAttribute.get_value('WELCOME_INSTAGRAM_URL') or '',
        youtube_url=SiteAttribute.get_value('WELCOME_YOUTUBE_URL') or ''
    )
    if form.validate_on_submit():
        attributes = [
            { 'name': 'HAS_WELCOME_MODAL', 'form_data': form.has_welcome_modal.data },
            { 'name': 'WELCOME_HEADER', 'form_data': form.header.data },
            { 'name': 'WELCOME_CONTENT', 'form_data': form.content.data },
            { 'name': 'WELCOME_ACTION', 'form_data': form.action.data },
            { 'name': 'WELCOME_FOOTER', 'form_data': form.footer.data },
            { 'name': 'WELCOME_WEBSITE_TEXT', 'form_data': form.website_text.data },
            { 'name': 'WELCOME_WEBSITE_URL', 'form_data': form.website_url.data },
            { 'name': 'WELCOME_EMAIL', 'form_data': form.email.data },
            { 'name': 'WELCOME_FACEBOOK_URL', 'form_data': form.facebook_url.data },
            { 'name': 'WELCOME_TWITTER_URL', 'form_data': form.twitter_url.data },
            { 'name': 'WELCOME_INSTAGRAM_URL', 'form_data': form.instagram_url.data },
            { 'name': 'WELCOME_YOUTUBE_URL', 'form_data': form.youtube_url.data },
        ]
        for attr in attributes:
            site_attr = SiteAttribute.get(attr['name'])
            site_attr.value = attr['form_data']
            db.session.add(site_attr)
        db.session.commit()
        flash('Welcome message successfully updated.', 'form-success')
    return render_template('admin/customize_site.html', app_name=SiteAttribute.get_value('ORG_NAME'), form=form)
