from flask import render_template
from flask.ext.login import (
    login_required,
)
from . import map


@map.route('/upload')
@login_required
def upload():
    """Upload CSV with new resources."""
    return render_template('map/upload.html')
