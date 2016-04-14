from flask import Blueprint

bulk_resource = Blueprint('bulk_resource', __name__)

from . import views  # noqa
