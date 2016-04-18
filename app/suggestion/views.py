from flask import render_template
from flask.ext.login import login_required
from . import suggestion
from ..models import Suggestion


@suggestion.route('/')
@login_required
def index():
    suggestions = Suggestion.query.all()
    return render_template('suggestion/index.html', suggestions=suggestions)


@suggestion.route('/suggest-new')
def suggest_new():
    return render_template('suggestion/suggest_new.html')
