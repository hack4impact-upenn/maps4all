from flask import Blueprint

admin_dashboard = Blueprint('admin_dashboard', __name__)

from . import views  # noqa