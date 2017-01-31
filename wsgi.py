from werkzeug.contrib.fixers import ProxyFix

from bijou.application import get_app, register_all_apps

application = get_app()
register_all_apps(application)

# log requests with proxyfix
application.wsgi_app = ProxyFix(application.wsgi_app)
