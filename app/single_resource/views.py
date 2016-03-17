from flask import render_template
from flask.ext.login import login_required
from . import single_resource

@single_resource.route('/')
@login_required
def index():
    return render_template('single_resource/index.html')
