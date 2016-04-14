from flask import render_template
from flask.ext.login import login_required
from . import suggestion


@suggestion.route('/')
@login_required
def index():
    return render_template('suggestion/index.html')


@suggestion.route('/suggest-new')
def suggest_new():
    return render_template('suggestion/suggest_new.html')
