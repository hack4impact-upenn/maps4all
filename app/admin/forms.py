from flask.ext.wtf import Form
from wtforms.fields import PasswordField, StringField, SubmitField, SelectField, TextField, TextAreaField
from wtforms.fields.html5 import EmailField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import InputRequired, Length, Email, EqualTo, Regexp, Optional
from flask_wtf.file import FileRequired, FileAllowed, FileField
from wtforms import ValidationError
from ..models import User, Role, EditableHTML
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

class NewPageForm(Form):
    editor_name = StringField('Page URL', validators=[InputRequired(),
                                                      Length(1,500),
                                                      Regexp(r'^[\w.@+-]+$')
                                                      ])
    page_name = StringField('Page Title', validators=[InputRequired(),
                                                      Length(1,500)])
    submit = SubmitField('Create Page')

class EditPageForm(Form):
    page_name = StringField('Page Title', validators=[InputRequired(),
                                                      Length(1,500)])
    submit = SubmitField('Edit Page Name')


class ChangeSiteNameForm(Form):
    site_name = StringField('Name', validators=[InputRequired(),
                                                Length(1, 30)])

    submit = SubmitField('Change name')


class ChangeTwilioCredentialsForm(Form):
    twilio_auth_token = StringField('Twilio Authentication Token',
        validators=[InputRequired(), Length(1, 64)])
    twilio_account_sid = StringField('Twilio Account SID',
        validators=[InputRequired(), Length(1, 64)])
    submit = SubmitField('Change Twilio credentials')


class WelcomeModalForm(Form):
    has_welcome_modal = StringField('Has Welcome Modal', validators=[InputRequired()])
    header = StringField('Header', validators=[Length(0, 200)])
    content = TextAreaField('Content', validators=[Length(0, 1000)])
    action = StringField('Action button text', validators=[Length(0, 200)])
    footer = StringField('Footer', validators=[Length(0, 200)])
    website_text = StringField('Website button text', validators=[Length(0, 50)])
    website_url = StringField('Website URL', validators=[Length(0, 200)])
    email = EmailField('Email address', validators=[Length(0, 200), Email(), Optional()])
    facebook_url = StringField('Facebook page URL', validators=[Length(0, 200)])
    twitter_url = StringField('Twitter page URL', validators=[Length(0, 200)])
    instagram_url = StringField('Instagram page URL', validators=[Length(0, 200)])
    youtube_url = StringField('YouTube channel URL', validators=[Length(0, 200)])
    submit = SubmitField('Save')

    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return False

        if self.website_url.data and self.website_text.data == '':
            self.website_text.errors.append('Include text for website button')
            return False

        return True
