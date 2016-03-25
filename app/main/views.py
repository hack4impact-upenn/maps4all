from flask import render_template
from . import main
from ..models import Resource
import json
from flask import jsonify

@main.route('/', methods=['GET'])
def index():
    return render_template('main/index.html')

@main.route('/get-resource', methods=['GET'])
def getResource():
    Resource.generate_fake()
    pins = Resource.query.all()
    data = []
    for pin in pins:
       this_pin = {'Name': pin.name, 'Latitude': pin.latitude, 'Longitude':
           pin.longitude}
       data.append(this_pin)
    print data
    return json.dumps(data)
