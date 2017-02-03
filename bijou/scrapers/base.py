from scrapers import RequestScraper


class Scraper(object):
    '''Scraping controller interface'''
    start_page_url = None
    scraper_cls = None

    def __init__(self, scraper_cls=RequestScraper):
        super().__init__()

        self.scraper_cls
        self.session = self.create_session()

    def run(self):
        '''Scraper runner'''
        self.scrape_categories(self.start_page_url)

    def parse(self, dom):
        pass

    def scrape(self, scraping_method):
        pass

    def scrape_category_listing(self, category_listing_url):
        '''Loop through categories given start url'''
        pass

    def scrape_category(self, category_url):
        '''Loop through all pages in category url and scrape products'''
        pass

    def parse_product(self):
        pass

    def parse_category(self):
        pass
