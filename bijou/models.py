import datetime

from flask_sqlalchemy import SQLAlchemy
from flask_user import UserMixin
from sqlalchemy_utils.types.choice import ChoiceType
from sqlalchemy_utils.types import JSONType

db = SQLAlchemy()


def DT_UTCNOW():
    # Prevent storing address of utcnow
    # Allowes to modify create date during tests
    return datetime.datetime.utcnow()


class BaseModel(db.Model):
    __abstract__ = True
    __searchable_fields__ = ()

    id = db.Column(db.Integer, primary_key=True)

    to_dict = lambda r: {c.name: str(getattr(r, c.name)) for c in r.__table__.columns}

    def __repr__(self):
        return '<{} id={}>'.format(self.__class__.__name__, self.id)

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self, data, save=True):
        changed = False
        for key, value in data.items():
            if hasattr(self, key) and getattr(self, key) != value:
                setattr(self, key, value)
                changed = True
        if changed and save:
            self.save()

    @classmethod
    def get(cls, **kwargs):
        return db.session.query(cls).filter_by(**kwargs).first()

    @classmethod
    def get_or_update(cls, defaults=None, **kwargs):
        instance = cls.get(**kwargs)
        if defaults is not None:
            kwargs.update(defaults)

        if instance is not None:
            instance.update(data=kwargs)
        else:
            instance = cls(**kwargs)
            instance.save()
        return instance


class Model(BaseModel):
    __abstract__ = True

    date_created = db.Column(db.DateTime, nullable=False, default=DT_UTCNOW)
    date_modified = db.Column(db.DateTime, nullable=False, default=DT_UTCNOW, onupdate=DT_UTCNOW)


class ScrapedModel(Model):
    __abstract__ = True

    item_id = db.Column(db.String(255), nullable=True, unique=True)
    url = db.Column(db.String(500), nullable=True)


class Client(Model):
    '''Client with online shops'''
    __tablename__ = 'client'

    name = db.Column(db.String(255), nullable=False)


class Shop(Model):
    '''Client's online shop'''
    __tablename__ = 'shop'

    client_id = db.Column(db.Integer, db.ForeignKey('client.id'))
    scraper = db.Column(db.String(64), nullable=True)
    # we can set here dynamic scraping settings
    # frequency = 10/day
    # workers_concurrency = 5

    def get_scraper_module(self):
        pass


class ShopCategory(ScrapedModel):
    '''Online shops category'''
    __tablename__ = 'shop_category'

    name = db.Column(db.String(128), unique=True)

    shop_id = db.Column(db.Integer, db.ForeignKey('shop.id'))
    parent_id = db.Column(db.Integer, db.ForeignKey('shop_category.id'), nullable=True)
    tag_id = db.Column(db.Integer, db.ForeignKey('tag.id'), nullable=True)

    def to_dict(self, with_relationships=False):
        result = super().to_dict()

        if with_relationships:
            result['products'] = [p.to_dict() for p in ShopProduct.query.filter_by(shop_category_id=self.id)]

        return result

    def __repr__(self):
        return '<{} id={} name={}>'.format(self.__class__.__name__, self.id, self.name)


class ShopProduct(ScrapedModel):
    '''Online shops product'''
    __tablename__ = 'shop_product'

    shop_id = db.Column(db.Integer, db.ForeignKey('shop.id'))
    shop_category_id = db.Column(db.Integer, db.ForeignKey('shop_category.id'), nullable=True)
    name = db.Column(db.String(128), nullable=True)
    description = db.Column(db.String(2000), nullable=True)
    price = db.Column(db.Float(), nullable=True)
    price_range = db.Column(db.String(64), nullable=True)
    sizes = db.Column(JSONType(), nullable=True)
    colors = db.Column(JSONType(), nullable=True)


class Tag(Model):
    '''Tags managed by us into which shop categories aggregate'''
    __tablename__ = 'tag'

    name = db.Column(db.String(255), nullable=False, unique=True)
    description = db.Column(db.String(1000), nullable=True)


class User(Model, UserMixin):
    __tablename__ = 'auth_user'

    username = db.Column(db.String(255), nullable=False, unique=True)
    email = db.Column(db.String(255), nullable=True, unique=True)
    first_name = db.Column(db.String(50), nullable=True)
    last_name = db.Column(db.String(50), nullable=True)
    is_enabled = db.Column(db.Boolean(), nullable=False, default=False)
    is_staff = db.Column(db.Boolean(), nullable=False, default=True)

    @property
    def is_active(self):
        return self.is_enabled

    @property
    def is_admin(self):
        return self.is_staff

    @property
    def name(self):
        return " ".join((self.first_name or "", self.last_name or "")).strip() or None

    @property
    def is_admin(self):
        return self.is_staff


class Swipe(Model):
    '''User individual swipe'''
    __tablename__ = 'swipe'

    TYPES = [
        (u'yes', u'Yes'),
        (u'no', u'No'),
        (u'pass', u'Pass')
    ]

    user_id = db.Column(db.Integer, db.ForeignKey('auth_user.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('shop_product.id'))
    choice = db.Column(ChoiceType(TYPES))
