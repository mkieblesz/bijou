from bijou.models import ShopProduct, ShopCategory
from bijou.scrapers.shops.farah import FarahScraper, FarahProductScraper
from bijou.testutils.cases import BaseScraperTestCase

PRODUCT_URL = 'http://www.farah.co.uk/clothing/knitwear/jumpers/the-mullen-merino-wool-jumper-F4GF4081GP.html?cgid=farahcaprljumpers&srule=best-matches&start=1&dwvar_F4GF4081GP_size=S&dwvar_F4GF4081GP_color=001'
PRICE_RANGE_PRODUCT_URL = 'http://www.farah.co.uk/clothing/shirts/the-brewer/the-brewer-slim-fit-shirt-F4WS4054GP.html'


class FarahScraperTest(BaseScraperTestCase):
    def test_simple(self):
        scraper = FarahScraper()
        scraper.run()
        assert len(ShopCategory.query.all()) == 5

        scraper.run()
        assert len(ShopCategory.query.all()) == 5


class FarahProductScraperTest(BaseScraperTestCase):
    def test_simple(self):
        scraper = FarahProductScraper(page_url=PRODUCT_URL)
        scraper.run()
        assert len(ShopProduct.query.all()) == 1

        scraper.run()
        assert len(ShopProduct.query.all()) == 1

    def test_product_price_range(self):
        scraper = FarahProductScraper(page_url=PRICE_RANGE_PRODUCT_URL)
        scraper.run()

        product = ShopProduct.query.all()[0]

        assert product.price is None, product.price
        assert product.price_range == '£38.50 - £55.00', product.price_range


class FarahProductListingScraperTest(BaseScraperTestCase):
    def test_simple(self):
        pass


class FarahCategoryScraperTest(BaseScraperTestCase):
    def test_simple(self):
        pass
