from ..decorators import admin_required

from flask import render_template, abort, redirect, flash, url_for
from flask.ext.login import login_required, current_user

from forms import (
    ChangeAccountTypeForm,
    ChangeUserEmailForm,
    EditDescriptorForm,
    InviteUserForm,
    NewDescriptorForm,
    NewUserForm
)
from . import admin
from ..models import User, Role, Descriptor
from .. import db
from ..email import send_email


@admin.route('/')
@login_required
@admin_required
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
        send_email(user.email,
                   'You Are Invited To Join',
                   'account/email/invite',
                   user=user,
                   user_id=user.id,
                   token=token)
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


@admin.route('/descriptors')
@login_required
@admin_required
def existing_descriptors():
    """View all resource descriptors."""
    descriptors = Descriptor.query.all()
    return render_template('admin/descriptors.html', descriptors=descriptors)


@admin.route('/new-descriptor', methods=['GET', 'POST'])
@login_required
@admin_required
def new_descriptor():
    """Create a new descriptor."""
    form = NewDescriptorForm()
    for i in range(10):
        form.option_values.append_entry()
    if form.validate_on_submit():
        values = []
        for v in form.option_values.data:
            if v is not None and len(v) != 0:
                values.append(v)
        print values
        descriptor = Descriptor(name=form.name.data, values=values)
        db.session.add(descriptor)
        db.session.commit()
        flash('Descriptor {} successfully created'.format(descriptor.name),
              'form-success')
        return redirect(url_for('admin.new_descriptor'))
    return render_template('admin/new_descriptor.html', form=form)


@admin.route('/descriptor/<int:desc_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_descriptor(desc_id):
    """Edit a new descriptor."""
    form = EditDescriptorForm()
    descriptor = Descriptor.query.filter_by(id=desc_id).first()
    is_option = len(descriptor.values) != 0

    if form.validate_on_submit():
        values = []
        for v in form.option_values.data:
            if v is not None and len(v) != 0:
                values.append(v)
        descriptor.name = form.name.data
        descriptor.values = values
        db.session.add(descriptor)
        db.session.commit()
        flash('Descriptor {} successfully editted'.format(descriptor.name),
              'form-success')
        return redirect(url_for('admin.existing_descriptors'))
    else:
        form.name.data = descriptor.name
        for i in range(10):
            if i < len(descriptor.values):
                form.option_values.append_entry(descriptor.values[i])
            else:
                form.option_values.append_entry()
    return render_template('admin/edit_descriptor.html', form=form,
                           is_option=is_option, desc_id=desc_id)


@admin.route('/descriptor/<int:desc_id>/delete')
@login_required
@admin_required
def delete_descriptor(desc_id):
    """Deletes a descriptor."""
    descriptor = Descriptor.query.filter_by(id=desc_id).first()
    db.session.delete(descriptor)
    db.session.commit()
    flash('Successfully deleted descriptor %s.' % descriptor.name, 'success')
    return redirect(url_for('admin.existing_descriptors'))
