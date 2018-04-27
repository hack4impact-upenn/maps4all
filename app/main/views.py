import json
import os
from twilio.rest.lookups import TwilioLookupsClient
from twilio.rest import TwilioRestClient
from flask import render_template, url_for, request, jsonify
from flask.ext.login import login_required
from twilio import twiml
from app import csrf
from .. import db
from ..models import EditableHTML, Resource, Rating, Descriptor, OptionAssociation, RequiredOptionDescriptor
from . import main
from wtforms.fields import SelectMultipleField, TextAreaField
from ..single_resource.forms import SingleResourceForm
from datetime import datetime

@main.route('/')
def index():
    req_opt_desc = RequiredOptionDescriptor.query.all()
    req_opt_id = -1
    if req_opt_desc:
        req_opt_desc = req_opt_desc[0]
        req_opt_desc = Descriptor.query.filter_by(
            id=req_opt_desc.descriptor_id
        ).first()
        if req_opt_desc is not None:
            req_opt_id = req_opt_desc.id
    options = Descriptor.query.all()
    options = [o for o in options if len(o.text_resources) == 0 and o.id != req_opt_id]
    options_dict = {}
    for o in options:
        options_dict[o.name] = o.values
    req_options = {}
    if req_opt_desc:
        for val in req_opt_desc.values:
            req_options[val] = False
    twilio_auth = False
    if os.environ.get('TWILIO_AUTH_TOKEN') is not None:
        twilio_auth = True
    return render_template('main/index.html', options=options_dict, req_options=req_options, req_desc=req_opt_desc, twilio_auth=twilio_auth)

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
    # case insensitive search
    resource_pool = Resource.query.filter(Resource.name.ilike('%{}%'.format(name))).all()
    req_opt_desc = RequiredOptionDescriptor.query.all()
    if req_opt_desc:
        req_opt_desc = req_opt_desc[0]
        req_opt_desc = Descriptor.query.filter_by(
            id=req_opt_desc.descriptor_id
        ).first()
    resources = []
    if req_opt_desc and len(req_options) > 0:
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
    opt_options = request.args.getlist('optoption')
    option_map = {}
    # Create a dict, option_map, that maps from option names to a list of user selected values
    for opt in opt_options:
        if opt != "null":
            option_val = opt.split(',')
            for opt_val in option_val:
                key_val = opt_val.split(':')
                if key_val[0] in option_map:
                    option_map[key_val[0]].append(key_val[1])
                else:
                    option_map[key_val[0]] = [key_val[1]]

    descriptors = Descriptor.query.all()
    new_pool = resource_pool
    if len(req_options) > 0:
        new_pool = resources
        resources = []
    # Iterate through resources and check that there's a match for all of the options
    # that the user selected. If there is, add that resource to the list of resources
    for resource in new_pool:
        number_of_options_found = 0
        for opt in list(option_map.keys()):
            opt_descriptors = OptionAssociation.query.filter_by(
                resource_id=resource.id
            )
            for desc in opt_descriptors:
                if desc.descriptor.name == opt:
                    if desc.descriptor.values[desc.option] in option_map[opt]:
                        number_of_options_found += 1
                        break
        if number_of_options_found == len(list(option_map.keys())):
            resources.append(resource)
    resources_as_dicts = Resource.get_resources_as_dicts(resources)
    return json.dumps(resources_as_dicts)


@main.route('/get-associations/<int:resource_id>')
def get_associations(resource_id):
    resource = Resource.query.get(resource_id)
    return json.dumps(Resource.get_associations(resource))


@main.route('/pages/<pageName>')
def render_page(pageName):
    editable_html_obj = EditableHTML.get_editable_html(pageName)
    return render_template('main/generalized_page.html',
                          editable=editable_html_obj)

@main.route('/about')
def about():
    editable_html_obj = EditableHTML.get_editable_html('about')
    if editable_html_obj is False:
        edit = EditableHTML(editor_name='about', page_name='About', value='')
        db.session.add(edit)
        db.session.commit()
        editable_html_obj = edit
    return render_template('main/about.html',
                           editable_html_obj=editable_html_obj)

@main.route('/overview')
@login_required
def overview():
    editable_html_obj = EditableHTML.get_editable_html('overview')
    if editable_html_obj is False:
        edit = EditableHTML(editor_name='overview', page_name='Overview', value='')
        db.session.add(edit)
        db.session.commit()
        editable_html_obj = edit
    return render_template('main/overview.html',
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
@main.route('/send-sms', methods=['POST'])
def send_sms():
    sid = os.environ.get('TWILIO_ACCOUNT_SID')
    auth = os.environ.get('TWILIO_AUTH_TOKEN')
    client = TwilioLookupsClient(account=sid, token=auth)
    send_client = TwilioRestClient(account=sid, token=auth)
    if request is not None:
        phone_num= request.json['number']
        resourceID = request.json['id']
        curr_res = Resource.query.get(resourceID)
        name = "Name: " + curr_res.name
        address = "Address: " + curr_res.address
        message = name +"\n" + address
        try:
            number = client.phone_numbers.get(phone_num, include_carrier_info=False)
            num = number.phone_number
            send_client.messages.create(
                to=num,
                from_="+17657692023",
                body=message)
            return jsonify(status='success')
        except:
            return jsonify(status='error')

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
