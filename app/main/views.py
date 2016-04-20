from flask import render_template, request
from . import main
from ..models import Resource
import json


@main.route('/', methods=['GET'])
def index():
    return render_template('main/index.html')


@main.route('/get-resource', methods=['GET'])
def get_resource():
    Resource.generate_fake()
    names = Resource.query.with_entities(Resource.name)
    lats = Resource.query.with_entities(Resource.latitude)
    longs = Resource.query.with_entities(Resource.longitude)
    data = []
    counter = 0
    for name in names:
        this_pin = {'Name': name, 'Latitude': lats[counter], 'Longitude':
            longs[counter]}
        counter = counter + 1
        data.append(this_pin)
    return json.dumps(data)


@main.route('/get-info', methods=['POST'])
def getInfo():
    pin_info = Resource.query.filter_by(name=request.form['data']).first()
    print type(pin_info.text_descriptors[0].text) #type: InstrumentedList of
    # TextAssociations
    return json.dumps({'Address': pin_info.address,
                       'Description': pin_info.text_descriptors[0].text})
