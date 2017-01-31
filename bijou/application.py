import atexit
import os

from werkzeug.exceptions import HTTPException

from flask import Flask
from flask_caching import Cache


def register_logging(app):
    return app


def register_exceptions(app):
    from bijou.exceptions import ErrorException, UncategorisedError

    def make_response(ex):
        if not isinstance(ex, ErrorException):
            ex = UncategorisedError(message=str(ex), status=(ex.code if isinstance(ex, HTTPException) else 500))

        # TODO: use Snetry instead
        log_message = str(ex)
        if ex.is_error():
            app.logger.exception(log_message)
        elif ex.is_info():
            app.logger.info(log_message)

        return ex.get_response()

    @app.errorhandler(Exception)
    def unhandled_exception(ex):
        return make_response(ex)

    return app


def register_exiting():
    def exiting():
        from flask import current_app as app
        app.logger.info('Exiting app...')
        return app

    atexit.register(exiting())


def register_endpoints(app):
    from bijou.api.endpoints import ModelEndpoint, SwipeEndpoint
    from bijou.models import db
    from bijou.web.views import HomeView

    # database
    db.session = db.create_scoped_session(options=app.config['SQLALCHEMY_SESSION_OPTIONS'])
    db.init_app(app)
    app.db = db

    # api endpoints
    app.add_url_rule('/<str:name>/<int:id>', view_func=ModelEndpoint.as_view('model'))
    app.add_url_rule('/<int:product_id>', view_func=SwipeEndpoint.as_view('swipe'))

    # web endpoints
    app.add_url_rule('/', view_func=HomeView.as_view('homeview'))

    return app


def register_cache(app):
    cache = Cache(app)
    app.cache = cache


def create_base_app():
    app = Flask(__name__)

    return app


def register_all_apps(app):
    register_logging(app)
    register_endpoints(app)
    register_exceptions(app)
    register_cache(app)


def get_app():
    from flask import current_app as app
    from .config.default import Config, base_dir

    if not app:
        app = create_base_app()

    app.config.from_object(Config)
    # environment config (tst/dev/stg/prd)
    app.config.from_pyfile(os.path.join(base_dir, 'config.cfg'), silent=True)

    return app


def get_test_app():
    from flask import current_app as app
    from .config.test_config import TestConfig

    if not app:
        app = create_base_app()

    app.config.from_object(TestConfig)
    register_all_apps(app)

    return app
