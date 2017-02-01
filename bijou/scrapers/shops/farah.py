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
        # if nothing selected it is tree root
        category_name = dom.select_one('.extended-text-content > .cat-container > h1').get_text('', strip=True)
        category = ShopCategory.get(name=category_name)

        if category is None:
            raise ParserException('Could not retrieve category form category listing')

        # there might be better way to do this
        is_leaf = False
        for cat_link in dom.select('.refineLink.active'):
            if len(cat_link.parent.select('.refineLink')) == 1 and cat_link.get_text('', strip=True) == category_name:
                is_leaf = True

        if is_leaf:
            # TODO: loop through the products and start product scrapers, ideally by manipulating get params
            # if self.paginate:
            #     for product_listing_url in product_page_generator():
            #         # don't paginate
            #         self.defer(FarahProductListingScraper, **{'page_url': product_listing_url, 'paginate': False})

            return {
                'product_pages': [
                    elem.get('href')
                    for elem in dom.select('div.productlisting div.name > a')
                ]
            }

        # if root category just get list
        if dom.select_one('ul.refinementcategory a.refineLink.active') is None:
            sub_categories = dom.select('ul.refinementcategory > li > a')
        # get lower most expanded tree
        else:
            sub_categories = [
                cat
                for cat in dom.select('ul.refinementcategory > li.expandable.active > ul.refinementcategory > li > a')
                if cat.select_one('ul.refinementcategory a.refineLink.active') is None
            ]

        return {
            'sub_categories': [
                {
                    'name': elem.get_text('', strip=True),
                    'shop_id': self.shop.id,
                    'parent_id': category.id,
                    'url': elem.get('href')
                }
                for elem in sub_categories
            ]
        }

        return {}

    def handle_result(self, result):
        for url in result.get('product_pages', []):
            self.defer(FarahProductScraper, **{'page_url': url})

        for data in result.get('sub_categories', []):
            kwargs = pop_kwargs(data, ['name', 'shop_id'])
            ShopCategory.get_or_update(defaults=data, **kwargs)

            self.defer(FarahCategoryScraper, **{'page_url': data['url']})


class FarahProductScraper(Scraper, FarahScraperMixin):
    '''Scrape product description page'''
    def parse(self, dom):
        # if nothing selected it is tree root
        product_pricing = dom.select_one('div.productinfopricing')
        category_link = dom.select('.breadcrumb > a')[0]

        category = ShopCategory.get(name=category_link.get_text('', strip=True))
        try:
            category.id
        except:
            import ipdb
            ipdb.set_trace()
        return {
            'shop_id': self.shop.id,
            'shop_category_id': category.id,
            'price': product_pricing.select_one('div.salesprice').get_text('', strip=True)[1:],
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
    def parse(self, dom):
        return {}

    def handle_result(self, result):
        pass
