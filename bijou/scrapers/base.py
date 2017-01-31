import json
from bs4 import BeautifulSoup

from bijou.exceptions import ParserException
from bijou.scrapers.methods import RequestMethod


class Scraper(object):
    '''Scraping controller interface. Each page type has it's own scraper controller'''

    page_url = None
    scraper_cls = RequestMethod

    def __init__(self, page_url=None, paginate=True):
        super().__init__()
        self.paginate = paginate

        if page_url is not None:
            self.page_url = page_url
        self.scraper = self.scraper_cls()

    def get_parser(self, response, html_parser='lxml', parse_only=None):
        return BeautifulSoup(response, html_parser, parse_only=parse_only)

    def get_json_parser(self, response):
        try:
            return json.loads(response)
        except ValueError:
            raise ParserException('Couldn\'t load json response')

    def run(self):
        '''Scraper runner'''
        response = self.scraper.get(self.page_url)
        dom = self.get_parser(response)
        result = self.parse(dom)

        self.handle_result(result)

    def defer(self, ScraperClass, *args, **kwargs):
        ScraperClass(*args, **kwargs).run()

    def handle_result(self, result):
        raise NotImplementedError('Implement')

    def parse(self, dom):
        raise NotImplementedError('Implement')

    def scrape(self, scraping_method):
        raise NotImplementedError('Implement')
