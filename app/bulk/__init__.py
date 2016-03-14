from flask import Blueprint

bulk = Blueprint('bulk', __name__)

from . import views  # noqa
