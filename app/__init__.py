import os
from flask import Flask
from flask.ext.mail import Mail
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from flask.ext.assets import Environment
from flask.ext.wtf import CsrfProtect
from flask.ext.compress import Compress
from flask.ext.rq import RQ

from config import config
from assets import app_css, app_js, vendor_css, vendor_js

basedir = os.path.abspath(os.path.dirname(__file__))

mail = Mail()
db = SQLAlchemy()
csrf = CsrfProtect()
compress = Compress()
# Set up Flask-Login
login_manager = LoginManager()
# TODO: Ideally this should be strong, but that led to bugs. Once this is
# fixed, switch protection mode back to 'strong'
login_manager.session_protection = 'basic'
login_manager.login_view = 'account.login'


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # Set up extensions
    mail.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    compress.init_app(app)
    RQ(app)

    # Register Jinja template functions
    from utils import register_template_utils
    register_template_utils(app)

    # Set up asset pipeline
    assets_env = Environment(app)
    dirs = ['assets/styles', 'assets/scripts']
    for path in dirs:
        assets_env.append_path(os.path.join(basedir, path))
    assets_env.url_expire = True

    assets_env.register('app_css', app_css)
    assets_env.register('app_js', app_js)
    assets_env.register('vendor_css', vendor_css)
    assets_env.register('vendor_js', vendor_js)

    # Configure SSL if platform supports it
    if not app.debug and not app.testing and not app.config['SSL_DISABLE']:
        from flask.ext.sslify import SSLify
        SSLify(app)

    # Create app blueprints
    from main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from account import account as account_blueprint
    app.register_blueprint(account_blueprint, url_prefix='/account')

    from admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint, url_prefix='/admin')

    from bulk_resource import bulk_resource as bulk_resource_blueprint
    app.register_blueprint(bulk_resource_blueprint,
                           url_prefix='/bulk-resource')

    from descriptor import descriptor as descriptor_blueprint
    app.register_blueprint(descriptor_blueprint, url_prefix='/descriptor')

    from single_resource import single_resource as single_resource_blueprint
    app.register_blueprint(single_resource_blueprint,
                           url_prefix='/single-resource')

    from suggestion import suggestion as suggestion_blueprint
    app.register_blueprint(suggestion_blueprint, url_prefix='/suggestion')

    return app
