from flask import render_template
from flask.ext.login import login_required
from . import descriptor

@descriptor.route('/')
@login_required
def index():
    return render_template('descriptor/index.html')
