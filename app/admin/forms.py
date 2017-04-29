from flask.ext.wtf import Form
from wtforms.fields import PasswordField, StringField, SubmitField
from wtforms.fields.html5 import EmailField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import InputRequired, Length, Email, EqualTo
from flask_wtf.file import FileRequired, FileAllowed, FileField
from wtforms import ValidationError
from ..models import User, Role
from .. import db


class ChangeUserEmailForm(Form):
    email = EmailField('New email', validators=[
        InputRequired(),
        Length(1, 500),
        Email()
    ])
    submit = SubmitField('Update email')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')


class ChangeAccountTypeForm(Form):
    role = QuerySelectField('New account type',
                            validators=[InputRequired()],
                            get_label='name',
                            query_factory=lambda: db.session.query(Role).
                            order_by('permissions'))
    submit = SubmitField('Update role')


class InviteUserForm(Form):
    role = QuerySelectField('Account type',
                            validators=[InputRequired()],
                            get_label='name',
                            query_factory=lambda: db.session.query(Role).
                            order_by('permissions'))
    first_name = StringField('First name', validators=[InputRequired(),
                                                       Length(1, 500)])
    last_name = StringField('Last name', validators=[InputRequired(),
                                                     Length(1, 500)])
    email = EmailField('Email', validators=[InputRequired(), Length(1, 500),
                                            Email()])
    submit = SubmitField('Invite')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')


class NewUserForm(InviteUserForm):
    password = PasswordField('Password', validators=[
        InputRequired(), EqualTo('password2',
                                 'Passwords must match.')
    ])
    password2 = PasswordField('Confirm password', validators=[InputRequired()])

    submit = SubmitField('Create')


class ChangeSiteNameForm(Form):
    site_name = StringField('Name', validators=[InputRequired(),
                                                Length(1, 30)])

    submit = SubmitField('Change name')


class ChangeSiteLogoForm(Form):
    site_logo = FileField(validators=[
        FileRequired(),
        FileAllowed(['jpg', 'png', 'gif', 'jpeg'],
                    'jpg, jpeg, png, or gif images only!')
    ])

    submit = SubmitField('Change logo')


class ChangeSiteStyleForm(Form):
    site_style = FileField(validators=[
        FileRequired(),
        FileAllowed(['css'], 'Please upload a .css file!')
    ])

    submit = SubmitField('Change stylesheet')
