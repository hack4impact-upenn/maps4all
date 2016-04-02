from flask import render_template
from . import main
from ..models import Resource
import json


@main.route('/', methods=['GET'])
def index():
    return render_template('main/index.html')


@main.route('/get-resource', methods=['GET'])
def get_resource():
    Resource.generate_fake()
    pins = Resource.query.all()
    data = []
    for pin in pins:
        this_pin = {
           'name': pin.name,
           'latitude': pin.latitude,
           'longitude': pin.longitude}
        data.append(this_pin)
    return json.dumps(data)
