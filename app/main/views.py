from flask import render_template
from . import main
from ..models import Descriptor


@main.route('/', methods=['GET'])
def index():
    print "getting filters"
    all_filters = Descriptor.query.all()
    top_filters = []
    advanced_filters = []
    if len(all_filters) > 3:
    	top_filters.append(all_filters[0].name)
    	top_filters.append(all_filters[1].name)
    	top_filters.append(all_filters[2].name)
    	for index in range(3, len(all_filters)):
    		advanced_filters.append(all_filters[index].name)
    else:
    	for filt in all_filters:
        	top_filters.append(filt.name)
    return render_template('main/index.html', top = top_filters, advanced = advanced_filters)