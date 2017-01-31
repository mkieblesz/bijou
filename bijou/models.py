import datetime

from flask_sqlalchemy import SQLAlchemy
from flask_user import UserMixin
from sqlalchemy_utils.types.choice import ChoiceType

db = SQLAlchemy()


def DT_UTCNOW():
    # Prevent storing address of utcnow
    # Allowes to modify create date during tests
    return datetime.datetime.utcnow()


class BaseModel(db.Model):
    __abstract__ = True
    __searchable_fields__ = ()

    id = db.Column(db.Integer, primary_key=True)

    def __repr__(self):
        return '<{} id={}>'.format(self.__class__.__name__, self.id)

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def save(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def bulk_save_objects(cls, objects):
        db.session.bulk_save_objects(objects=objects)
        db.session.commit()

    @classmethod
    def bulk_insert_mappings(cls, mappings):
        db.session.bulk_insert_mappings(cls, mappings)
        db.session.commit()

    @classmethod
    def bulk_update_mappings(cls, mappings):
        db.session.bulk_update_mappings(cls, mappings)
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


class Model(BaseModel):
    __abstract__ = True

    date_created = db.Column(db.DateTime, nullable=False, default=DT_UTCNOW)
    date_modified = db.Column(db.DateTime, nullable=False, default=DT_UTCNOW, onupdate=DT_UTCNOW)


class ScrapedModel(Model):
    __abstract__ = True

    item_id = db.Column(db.String(255), nullable=False, unique=True)


class Client(Model):
    '''Client with online shops'''
    __tablename__ = 'client'
    pass


class Shop(Model):
    '''Client's online shop'''
    __tablename__ = 'shop'

    # client = ...
    pass


class ShopCategory(ScrapedModel):
    '''Online shops category'''
    __tablename__ = 'shop_category'

    shop_id = db.Column(db.Integer, db.ForeignKey('shop.id'))
    # shop = ...
    # tag = ...

    # parent = ...
    # description = ...
    pass


class ShopProduct(ScrapedModel):
    '''Online shops product'''
    __tablename__ = 'shop_product'

    shop_id = db.Column(db.Integer, db.ForeignKey('shop.id'))
    shop_category_id = db.Column(db.Integer, db.ForeignKey('shop_category.id'), nullable=True)

    description = db.Column(db.String(1000), nullable=True)
    price = db.Column(db.Float(), nullable=True)
    sizes = db.Column(db.Float(), nullable=True)
    colors = db.Column(db.Float(), nullable=True)
    sizes = {
        'xs': ['xs']
    }
    colors = {
        'black': ['product_img_url', 'color_img_url', 'color_title']
    }
    pass


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


class Swipe(Model):
    '''User individual swipe'''
    __tablename__ = 'swipe'

    TYPES = [
        (u'yes', u'Yes'),
        (u'no', u'No'),
        (u'pass', u'Pass')
    ]

    user_id = db.Column(db.Integer, db.ForeignKey('person.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('person.id'))
    choice = db.Column(ChoiceType(TYPES))
