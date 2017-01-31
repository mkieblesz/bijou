from flask import jsonify


class SpiderException(Exception):
    message = None

    def __init__(self, message=None, status=None):
        if message is not None:
            self.message = message


class RetryLimitException(SpiderException):
    code = 15011
    status = 500
    message = 'Could not scrape page'


class ConnectionRefusedError(SpiderException):
    '''Throw when scraper has problem with creating session/refused connection with given url'''
    code = 15002
    status = 504
    message = 'Connection refused'


class ApiException(Exception):
    status = None
    message = None
    code = None

    def __init__(self, message=None, status=None):
        if message is not None:
            self.message = message
        if status is not None:
            self.status = status

    def is_error(self):
        return self.status >= 500

    def get_response(self):
        response = jsonify({
            'error': {
                'code': self.code,
                'message': self.message,
                'status': self.status
            }
        })
        response.status_code = self.status
        return response


class UncategorisedException(ApiException):
    '''Throw on all unhandled exceptions'''
    code = 15001
    status = 500
    message = 'Unrecognized exception'


class WebException(Exception):
    template = 'error.html'
    context = {}

    def __init__(self, context=None):
        if context is not None:
            self.context = context

    def get_response(self):
        return str(self)
        # render(self.template, self.context)
