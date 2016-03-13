from flask import Blueprint

map = Blueprint('map', __name__)

from . import views  # noqa
