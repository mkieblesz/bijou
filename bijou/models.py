class Client:
    '''Client with online shops'''
    pass


class Shop:
    '''Client's online shop'''
    # client = ...
    pass


class ShopCategory:
    '''Online shops category'''
    # shop = ...
    # tag = ...

    # parent = ...
    # description = ...
    pass


class ShopProduct:
    '''Online shops product'''
    # shop = ...
    # shop_category = ...

    # item_id = ...
    # description = ...
    # price = ...
    # promotion = ...
    sizes = {
        'xs'
    }
    colors = {
        'black': ['product_img_url', 'color_img_url', 'color_title']
    }
    pass


class Tag:
    '''Tags managed by us into which shop categories aggregate'''
    # description = ...
    pass


class User:
    '''Our user'''
    pass


class SwipeChoice(object):
    YES = 0
    NO = 1
    PASS = 2

    @classmethod
    def as_choices(cls):
        return (
            (cls.YES, 'yes'),
            (cls.NO, 'no'),
            (cls.PASS, 'pass')
        )


class Swipe:
    '''User individual swipe'''
    # user = ...
    # product = ...
    # choice = ...
    pass
