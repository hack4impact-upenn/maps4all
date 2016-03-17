from flask import Blueprint

suggestion = Blueprint('suggestion', __name__)

from . import views  # noqa
