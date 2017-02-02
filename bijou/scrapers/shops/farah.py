from urllib.parse import urlparse

from bijou.exceptions import ParserException
from bijou.models import Shop, ShopCategory, ShopProduct
from bijou.scrapers.base import Scraper


def pop_kwargs(result, list_of_args):
    kwargs = {}
    for arg_name in list_of_args:
        kwargs[arg_name] = result.pop(arg_name)
    return kwargs


class FarahScraperMixin(object):
    def __init__(self, *args, **kwargs):
        # do it with module introspection
        self.shop = Shop.get(scraper='farah')


class FarahScraper(Scraper, FarahScraperMixin):
    '''
    Entrypoint scraper, scrapes root categories.

    1. Enter home page.
    2. Scrape home categories.
    3. Enter each home category and scrape it's descendants.
    4. When leaf is reached scrape all products by iterating over all pages.
    '''
    page_url = 'http://www.farah.co.uk/'

    def parse(self, dom):
        return [
            {
                'name': elem.get_text('', strip=True),
                'shop_id': self.shop.id,
                'url': elem.get('href')
            }
            for elem in dom.select('div.categorymenu > #primaryNavigationList > li > a')
            if elem.get_text('', strip=True) not in ['New', 'Classic', 'Sale', 'BLOG']
        ]

    def handle_result(self, result):
        root_category = ShopCategory.get_or_update(name='Home', shop_id=self.shop.id, defaults={'url': self.page_url})
        root_category.save()

        # TODO: use bulk update
        for data in result:
            ShopCategory.get_or_update(parent_id=root_category.id, **data)
            self.defer(FarahCategoryScraper, **{'page_url': data['url']})


class FarahCategoryScraper(Scraper, FarahScraperMixin):
    '''Scrape left sidebar category tree and all products if leaf'''

    def parse(self, dom):
        category_name = dom.select('.breadcrumb > a')[-1].get_text('', strip=True)
        category = ShopCategory.get(name=category_name)

        if category is None:
            raise ParserException('Could not retrieve category form category listing')

        is_leaf = dom.select_one('ul.refinementcategory a.refineLink') is None
        if not is_leaf:
            for cat_link in dom.select('.refineLink.active'):
                if len(cat_link.parent.select('.refineLink')) == 1 and cat_link.get_text('', strip=True) == category_name:
                    is_leaf = True

        if is_leaf:
            # TODO: make pages as big as possible, good candidate for new scraper (if there will be a lot of pages
            # synchronous calling will cause problems + all pages might not display on same page)
            # first page
            self.defer(FarahProductListingScraper, **{'page_url': self.page_url, 'dom': dom})
            # next pages
            for page_link in dom.select('.searchresultsfooter .pagination li a'):
                self.defer(FarahProductListingScraper, **{'page_url': page_link.get('href')})

            return []

        if dom.select_one('ul.refinementcategory a.refineLink.active') is None:
            sub_categories = dom.select('ul.refinementcategory > li > a')
        else:
            sub_categories = [
                cat
                for cat in dom.select('ul.refinementcategory > li.expandable.active > ul.refinementcategory > li > a')
                if cat.select_one('ul.refinementcategory a.refineLink.active') is None
            ]

        return [
            {
                'name': elem.get_text('', strip=True),
                'shop_id': self.shop.id,
                'parent_id': category.id,
                'url': elem.get('href')
            }
            for elem in sub_categories
        ]

    def handle_result(self, result):
        for data in result:
            kwargs = pop_kwargs(data, ['name', 'shop_id'])
            ShopCategory.get_or_update(defaults=data, **kwargs)

            self.defer(FarahCategoryScraper, **{'page_url': data['url']})


class FarahProductScraper(Scraper, FarahScraperMixin):
    '''Scrape product description page'''

    def parse(self, dom):
        product_pricing = dom.select_one('div.productinfopricing')
        category_link = dom.select('.breadcrumb > a')[-1]

        category = ShopCategory.get(name=category_link.get_text('', strip=True))
        price = product_pricing.select_one('div.salesprice')
        price_range = product_pricing.select_one('div.price')

        return {
            'shop_id': self.shop.id,
            'shop_category_id': category.id if category is not None else None,
            'price': str(price.get_text('', strip=True)[1:]) if price is not None else None,
            'price_range': price_range.get_text(' ', strip=True) if price_range is not None else None,
            'item_id': product_pricing.select_one('span[itemprop="productID"]').get('data-master-id'),
            # name, avatar_bg, product_img
            'colors': [
                [
                    elem.select_one('a').get('title'),
                    elem.get('style').split('background: url("')[1][:-3],
                    # product image
                ]
                for elem in dom.select('div.swatches.color > swatchesdisplay > li')
            ],
            'sizes': [
                [
                    elem.select_one('a').get('title'),
                ]
                for elem in dom.select('div.swatches.size > swatchesdisplay > li')
            ],
            # 'description': strip html tags
            # promotion_text
            # price_before_promotion
        }

    def handle_result(self, data):
        kwargs = pop_kwargs(data, ['item_id', 'shop_id'])
        ShopProduct.get_or_update(defaults=data, **kwargs)


class FarahProductListingScraper(Scraper, FarahScraperMixin):
    '''Single category products - only leafs since parent information is in category tree'''

    def parse_item_id_from_url(self, url):
        # example path: clothing/polo-shirts/plain/the-blaney-short-sleeve-polo-shirt-F4KS5050GP.html
        return urlparse(url).path.split('-')[-1].split('.')[0]

    def parse(self, dom):
        # avoid scraping duplicate products (same product displayed many times under different color)
        return [
            elem.get('href')
            for elem in dom.select('div.productlisting div.name > a')
            if ShopProduct.get(item_id=self.parse_item_id_from_url(elem.get('href'))) is None
        ]

    def handle_result(self, result):
        for url in result:
            self.defer(FarahProductScraper, **{'page_url': url})
