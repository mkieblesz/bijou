import atexit
import os

from werkzeug.exceptions import HTTPException

from flask import Flask


def register_logging(app):
    return app


def register_exceptions(app):
    from bijou.exceptions import ApiException, UncategorisedException

    def make_response(ex):
        if not isinstance(ex, ApiException):
            ex = UncategorisedException(message=str(ex), status=(ex.code if isinstance(ex, HTTPException) else 500))

        # TODO: use Snetry instead
        log_message = str(ex)
        if ex.is_error():
            app.logger.exception(log_message)
        else:
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


def register_db(app):
    from bijou.models import db

    db.session = db.create_scoped_session(options=app.config['SQLALCHEMY_SESSION_OPTIONS'])
    db.init_app(app)
    db.create_all()
    app.db = db

    return app


def register_endpoints(app):
    from bijou.api.endpoints import ModelEndpoint, SwipeEndpoint
    from bijou.web.views import HomeView, ScrapeStreamView, ScrapeView

    # api endpoints
    app.add_url_rule('/swipe/<int:product_id>', view_func=SwipeEndpoint.as_view('swipe'))
    app.add_url_rule('/<name>/<int:id>', view_func=ModelEndpoint.as_view('model'))
    app.add_url_rule('/<name>', view_func=ModelEndpoint.as_view('model_list'))

    # web endpoints
    app.add_url_rule('/', view_func=HomeView.as_view('homeview'))
    app.add_url_rule('/stream', view_func=ScrapeStreamView.as_view('scrapestreamview'))
    app.add_url_rule('/scrape', view_func=ScrapeView.as_view('scrapeview'))

    return app


def create_base_app():
    app = Flask(__name__)

    return app


def register_all_apps(app):
    register_logging(app)
    register_db(app)
    register_endpoints(app)
    register_exceptions(app)


def get_app():
    from flask import current_app as app
    from .config.default import Config, base_dir

    if not app:
        app = create_base_app()

    app.config.from_object(Config)
    # environment config (tst/dev/stg/prd)
    app.config.from_pyfile(os.path.join(base_dir, 'config.cfg'), silent=True)

    return app


def get_registered_app():
    app = get_app()
    register_all_apps(app)
    return app


def get_test_app():
    from flask import current_app as app
    from .config.test_config import TestConfig

    if not app:
        app = create_base_app()

    app.config.from_object(TestConfig)
    register_all_apps(app)

    return app
