import inspect
import os
import unittest
import vcr

from flask import current_app

from bijou.config.default import base_dir
from bijou.models import Client, Shop
from bijou.scrapers.shops.farah import (
    FarahScraper,
    FarahProductScraper,
    FarahCategoryScraper,
    FarahProductListingScraper
)


class VCRMixin(object):
    '''A TestCase mixin that provides VCR integration.'''

    vcr_enabled = True
    cassette_dir = os.path.join(base_dir, 'tests', 'data')

    def setUp(self):
        super(VCRMixin, self).setUp()
        if self.vcr_enabled:
            kwargs = {'cassette_library_dir': self.cassette_dir}
            myvcr = self._get_vcr(**kwargs)
            cm = myvcr.use_cassette(self._get_cassette_name())
            self.cassette = cm.__enter__()
            self.addCleanup(cm.__exit__, None, None, None)

    def _get_vcr(self, **kwargs):
        if 'cassette_library_dir' not in kwargs:
            kwargs['cassette_library_dir'] = self._get_cassette_library_dir()
        return vcr.VCR(**kwargs)

    def _get_vcr_kwargs(self, **kwargs):
        return kwargs

    def _get_cassette_library_dir(self):
        testdir = os.path.dirname(inspect.getfile(self.__class__))
        return os.path.join(testdir, 'cassettes')

    def _get_cassette_name(self):
        return '{0}.{1}.yaml'.format(self.__class__.__name__, self._testMethodName)


class VCRTestCase(VCRMixin, unittest.TestCase):
    pass


class BaseScraperTestCase(VCRTestCase):
    def setUp(self):
        super().setUp()

        current_app.db.create_all()

        client = Client(name='Farah')
        client.save()
        shop = Shop(client_id=client.id, scraper='farah')
        shop.save()

        function_patches = [
            'bijou.scrapers.shops.farah.FarahScraper.defer',
            'bijou.scrapers.shops.farah.FarahProductScraper.defer',
            'bijou.scrapers.shops.farah.FarahProductListingScraper.defer',
            'bijou.scrapers.shops.farah.FarahCategoryScraper.defer',
        ]
        for defer_func in function_patches:
            class_patch = unittest.mock.patch(defer_func, side_effect=unittest.mock.Mock())
            self.addCleanup(class_patch.stop)
            class_patch.start()

    def tearDown(self):
        super().tearDown()
        current_app.db.session.remove()
        current_app.db.drop_all()
