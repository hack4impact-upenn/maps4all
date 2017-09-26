import os, json, boto3
from flask import url_for
from .models import EditableHTML, SiteAttribute
from werkzeug.utils import secure_filename
from uuid import uuid4


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
        return dict(site_name=SiteAttribute.get_value("ORG_NAME"),
                    logo_url=SiteAttribute.get_value("SITE_LOGO"),
                    style_timestamp=SiteAttribute.get_value("STYLE_TIME"),
                    style_sheet=SiteAttribute.get_value("STYLE_SHEET"))

    app.add_template_global(index_for_role)


    @app.template_filter('pages')
    def inject_pages(s):
        pages = EditableHTML.query.order_by(EditableHTML.page_name)
        pages_list = [p.__dict__ for p in pages]
        return pages_list



def index_for_role(role):
    return url_for(role.index)

def s3_upload(source_file, acl='public-read'):

    # Load necessary information into the application
    S3_KEY = os.environ.get('S3_KEY')
    S3_SECRET = os.environ.get('S3_SECRET')
    S3_BUCKET = os.environ.get('S3_BUCKET')
    S3_REGION = os.environ.get('S3_REGION')
    TARGET_FOLDER = ''

    source_filename = secure_filename(source_file.data.filename)
    source_extension = os.path.splitext(source_filename)[1]

    destination_filename = uuid4().hex + source_extension

    # Connect to S3 and upload file.
    s3 = boto3.client(
        's3',
        aws_access_key_id=S3_KEY,
        aws_secret_access_key=S3_SECRET,
    )

    try:
        s3.upload_fileobj(
            source_file.data,
            S3_BUCKET,
            source_filename,
            ExtraArgs = {
                "ACL": "public-read"
            }
        )

    except Exception as e:
        print("Error: ", e)
        return e

    return destination_filename


