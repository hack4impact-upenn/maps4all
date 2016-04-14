from flask import Blueprint

single_resource = Blueprint('single_resource', __name__)

from . import views  # noqa
