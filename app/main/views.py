from flask import render_template, request
from . import main
from ..models import Resource
import json


@main.route('/')
def index():
    return render_template('main/index.html')


@main.route('/get-resources')
def get_resources():
    resources = Resource.query.all() 
    resources_as_dicts = Resource.get_resources_as_dicts(resources)
    return json.dumps(resources_as_dicts)


@main.route('/get-associations/<int:resource_id>')
def get_associations(resource_id):
    pin_info = Resource.query.filter_by(id=resource_id).first()
    associations = {}
    for pin in pin_info.text_descriptors:
        associations[pin.descriptor.name] = pin.text
    for pin in pin_info.option_descriptors:
        associations[pin.descriptor.name] = pin.descriptor.values[pin.option]
    return json.dumps(associations)

