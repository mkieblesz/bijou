from werkzeug.contrib.fixers import ProxyFix

from bijou.application import get_registered_app

application = get_registered_app()

# log requests with proxyfix
application.wsgi_app = ProxyFix(application.wsgi_app)
