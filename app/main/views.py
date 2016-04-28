from flask import render_template
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


 # TODO: write logic to retrieve and return associations for resource.
@main.route('/get-associations/<int:resource_id>')
def get_associations(resource_id):
    pin_info = Resource.query.filter_by(name=request.form['data']).first()
    for pin in pin_info.text_descriptors:
        print pin
    return json.dumps({'Address': pin_info.address,
                       'Description': pin_info.text_descriptors[0].text})
    #associations = []
    #return json.dumps(associations)
