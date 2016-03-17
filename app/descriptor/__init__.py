from flask import Blueprint

descriptor = Blueprint('descriptor', __name__)

from . import views  # noqa
