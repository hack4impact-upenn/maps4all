from flask import url_for
from .models import SiteAttribute


def register_template_utils(app):
    """Register Jinja 2 helpers (called from __init__.py)."""

    @app.template_test()
    def equalto(value, other):
        return value == other

    @app.template_global()
    def is_hidden_field(field):
        from wtforms.fields import HiddenField
        return isinstance(field, HiddenField)

    @app.context_processor
    def inject_name():
        return dict(site_name=SiteAttribute.get_value("ORG_NAME"))

    app.add_template_global(index_for_role)


def index_for_role(role):
    return url_for(role.index)
