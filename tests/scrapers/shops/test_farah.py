from bijou.models import ShopProduct, ShopCategory
from bijou.scrapers.shops.farah import (
    FarahScraper,
    FarahProductScraper,
    FarahCategoryScraper,
    FarahProductListingScraper
)
from bijou.testutils.cases import BaseScraperTestCase

PRODUCT_URL = 'http://www.farah.co.uk/clothing/knitwear/jumpers/the-mullen-merino-wool-jumper-F4GF4081GP.html?cgid=farahcaprljumpers&srule=best-matches&start=1&dwvar_F4GF4081GP_size=S&dwvar_F4GF4081GP_color=001'


class FarahScraperTest(BaseScraperTestCase):
    def test_simple(self):
        scraper = FarahScraper()
        scraper.run()
        assert len(ShopCategory.query.all()) == 4

        scraper.run()
        assert len(ShopCategory.query.all()) == 4


class FarahProductScraperTest(BaseScraperTestCase):
    def test_simple(self):
        scraper = FarahProductScraper(page_url=PRODUCT_URL)
        scraper.run()

        assert len(ShopProduct.query.all()) == 1


class FarahProductListingScraperTest(BaseScraperTestCase):
    def test_simple(self):
        pass


class FarahCategoryScraperTest(BaseScraperTestCase):
    def test_simple(self):
        pass
