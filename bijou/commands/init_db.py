from flask import current_app
from flask_script.commands import Command

from bijou.application import get_registered_app
from bijou.models import Shop, Client


class InitDBCommand(Command):
    def run(self, *args, **kwargs):
        app = get_registered_app()

        with app.app_context():
            current_app.db.create_all()

        client = Client(name='Farah')
        client.save()

        shop = Shop(client_id=client.id, scraper='farah')
        shop.save()
