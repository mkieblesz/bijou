class BaseScraper(object):
    '''Scraping method interface'''
    pass


class RequestScraper(BaseScraper):
    '''Scraping method using simple HTTP requests'''
    pass


class BrowserScraper(BaseScraper):
    '''Scraping method using webkit-server'''
    pass
