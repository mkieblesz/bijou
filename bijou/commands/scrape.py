import importlib
from flask_script.commands import Command, Option

from bijou.application import get_registered_app


class ScrapeCommand(Command):
    option_list = (
        Option('-s', '--scraper', default='farah', required=False),
    )

    def run(self, *args, **kwargs):
        app = get_registered_app()

        with app.app_context():
            scraper_name = kwargs.get('scraper')
            scraper_module = importlib.import_module('bijou.scrapers.shops.{}'.format(scraper_name))
            # entry point scraper
            scraper = getattr(scraper_module, '{}Scraper'.format(scraper_name.title()))()

            print('Started scraper')
            scraper.run()
            print('Finished')
