from flask import url_for
from models import EditableHTML

def register_template_utils(app):
    """Register Jinja 2 helpers (called from __init__.py)."""

    @app.template_test()
    def equalto(value, other):
        return value == other

    @app.template_global()
    def is_hidden_field(field):
        from wtforms.fields import HiddenField
        return isinstance(field, HiddenField)

    app.add_template_global(index_for_role)


    @app.template_filter('pages')
    def inject_pages(s):
        pages = EditableHTML.query.order_by(EditableHTML.page_name)
        pages_list = [p.__dict__ for p in pages]
        return pages_list



def index_for_role(role):
    return url_for(role.index)
