import json

from flask import render_template, redirect, request
from flask.ext.login import login_required
from flask.ext.rq import get_queue

from .. import db
from ..models import EditableHTML, Resource
from . import main
from forms import ContactForm
from ..email import send_email

@main.route('/')
def index():
    return render_template('main/index.html')


@main.route('/get-resources')
def get_resources():
    resources = Resource.query.all()
    resources_as_dicts = Resource.get_resources_as_dicts(resources)
    return json.dumps(resources_as_dicts)

@main.route('/search-resources/<query_name>')
def search_resources(query_name):
    resources = Resource.query.filter(Resource.name.contains(query_name))
    resources_as_dicts = Resource.get_resources_as_dicts(resources)
    return json.dumps(resources_as_dicts)

@main.route('/get-associations/<int:resource_id>')
def get_associations(resource_id):
    resource = Resource.query.get(resource_id)
    associations = {}
    if resource is None:
        return json.dumps(associations)
    for td in resource.text_descriptors:
        associations[td.descriptor.name] = td.text
    for od in resource.option_descriptors:
        associations[od.descriptor.name] = od.descriptor.values[od.option]
    return json.dumps(associations)


@main.route('/about')
def about():
    editable_html_obj = EditableHTML.get_editable_html('about')
    return render_template('main/about.html',
                           editable_html_obj=editable_html_obj)


@main.route('/contact', methods=['GET', 'POST'])
def contact():
    editable_html_obj = EditableHTML.get_editable_html('contact')
    form = ContactForm()
    contact_email = 'maps4all.team@gmail.com'
    if form.validate_on_submit():
        print('sending email')
        get_queue().enqueue(
            send_email,
            to=contact_email,
            subject=form.category.data,
            template='email/contact',
            name=form.name.data,
            email=form.email.data,
            message=form.message.data
        )
        return redirect(url_for('main.index'))

    return render_template('main/contact.html',
                           editable_html_obj=editable_html_obj,
                           form=form)


@main.route('/update-editor-contents', methods=['POST'])
@login_required
def update_editor_contents():
    """Update the contents of an editor."""

    edit_data = request.form.get('edit_data')
    editor_name = request.form.get('editor_name')

    editor_contents = EditableHTML.query.filter_by(
        editor_name=editor_name).first()
    if editor_contents is None:
        editor_contents = EditableHTML(editor_name=editor_name)
    editor_contents.value = edit_data

    db.session.add(editor_contents)
    db.session.commit()

    return 'OK', 200

@main.route('/resource-view')
def resource():
    return render_template('main/resource.html')
