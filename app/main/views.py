from flask import render_template
from . import main
from ..models import Descriptor


@main.route('/', methods=['GET'])
def index():
    print "getting filters"
    all_filters = Descriptor.query.all()
    filter_names = []
    for filt in all_filters:
        filter_names.append(filt.name)
    return render_template('main/index.html', filters = filter_names)