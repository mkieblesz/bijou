import os

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))


class Config(object):
    SQLALCHEMY_DATABASE_URI = 'postgresql://bijou:bijou@localhost:5432/bijou'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_SESSION_OPTIONS = {}
