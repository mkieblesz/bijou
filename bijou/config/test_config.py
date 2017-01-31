import os

from bijou.config.default import Config, base_dir

test_data_dir = os.path.join(base_dir, 'tests', 'data')

os.makedirs(test_data_dir, exist_ok=True)


class TestConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/test.db'
