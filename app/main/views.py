import json

from flask import render_template, request,jsonify
from flask import render_template, url_for, request, jsonify
from flask.ext.login import login_required

from app import csrf
from .. import db
from ..models import EditableHTML, Resource, Rating, Descriptor, OptionAssociation, RequiredOptionDescriptor
from . import main
from datetime import datetime

@main.route('/')
def index():
    req_opt_desc = RequiredOptionDescriptor.query.all()[0]
    req_opt_desc = Descriptor.query.filter_by(
        id=req_opt_desc.descriptor_id
    ).first()
    req_options = {}
    if req_opt_desc is not None:
        for val in req_opt_desc.values:
            req_options[val] = False
    return render_template('main/index.html', req_options=req_options, req_desc=req_opt_desc)

@main.route('/get-resources')
def get_resources():
    resources = Resource.query.all()
    resources_as_dicts = Resource.get_resources_as_dicts(resources)
    return json.dumps(resources_as_dicts)

@main.route('/search-resources')
def search_resources():
    name = request.args.get('name')
    if name is None:
        name = ""
    req_options = request.args.getlist('reqoption')
    if req_options is None:
        req_options = []
    resource_pool = Resource.query.filter(Resource.name.contains(name)).all()
    req_opt_desc = RequiredOptionDescriptor.query.all()[0]
    req_opt_desc = Descriptor.query.filter_by(
        id=req_opt_desc.descriptor_id
    ).first()
    resources = list(resource_pool)
    if req_opt_desc is not None and len(req_options) > 0:
        resources = []
        int_req_options = []
        for o in req_options:
            int_req_options.append(req_opt_desc.values.index(str(o)))
        for resource in resource_pool:
            associations = OptionAssociation.query.filter_by(
                resource_id=resource.id,
                descriptor_id=req_opt_desc.id
            )
            for a in associations:
                if a.option in int_req_options:
                    resources.append(resource)
                    break
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

@csrf.exempt
@main.route('/rating-post', methods =['POST'])
def post_rating():
    if request is not None:
            time = datetime.now()
            star_rating = request.json['rating']
            comment = request.json['review']
            resourceID = request.json['id']
            if comment and star_rating:
                rating = Rating(submission_time=time,
                                rating=star_rating,
                                review=comment,
                                resource_id=resourceID)
                db.session.add(rating)
                db.session.commit()
            elif star_rating:
                rating = Rating(submission_time=time,
                                rating=star_rating,
                                resource_id=resourceID)
                db.session.add(rating)
                db.session.commit()
    return jsonify(status='success')

