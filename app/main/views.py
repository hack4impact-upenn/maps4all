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
    resource = Resource.query.get(resource_id)
    associations = {}
    if resource is None: return json.dumps(associations)
    for descriptor in resource.text_descriptors:
        associations[descriptor.descriptor.name] = descriptor.text
    for descriptor in resource.option_descriptors:
        associations[descriptor.descriptor.name] = descriptor.descriptor.values[
            descriptor.option]
    return json.dumps(associations)

