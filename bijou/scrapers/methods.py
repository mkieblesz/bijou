import requests
from bijou.constants import REQUEST_METHOD_RETRIES
from bijou.exceptions import RetryLimitException


class BaseMethod(object):
    '''Scraping method interface'''

    def __init__(self):
        super().__init__()

        self.session = self.create_session()

    def create_session(self):
        raise NotImplementedError('Implement')

    def reset_session(self):
        raise NotImplementedError('Implement')

    def get(self):
        raise NotImplementedError('Implement')

    def submit(self):
        raise NotImplementedError('Implement')


class RequestMethod(BaseMethod):
    '''Scraping method using simple HTTP requests'''

    def create_session(self):
        '''Reuse TCP connection for faster scraping'''
        return requests.Session()

    def reset_session(self):
        self.session = requests.Session()

    def generic(self, method, url, retry=1, **kwargs):
        if retry == REQUEST_METHOD_RETRIES:
            raise RetryLimitException('Could not get {}'.format(url))

        try:
            response = getattr(self.session, method)(url, **kwargs)
        except:
            retry += 1
            # reset TCP session
            self.reset_session()
            response = super().generic(method, url, retry=retry)

        return response.text

    def get(self, url):
        return self.generic("get", url)

    def submit(self, url, data):
        kwargs = {'data': data}
        return self.generic("post", url, **kwargs)


class BrowserMethod(BaseMethod):
    '''Scraping method using webkit-server'''
    # TODO: implement browser scraping
    pass
