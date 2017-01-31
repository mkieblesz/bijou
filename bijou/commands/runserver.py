from flask_script.commands import Command, Option

from bijou.application import get_registered_app


class RunServerCommand(Command):
    option_list = (
        Option('-d', '--debug', action='store_true', default=False, required=False),
    )

    def run(self, *args, **kwargs):
        app = get_registered_app()

        app.run(host='0.0.0.0', port=5000, debug=kwargs.get('debug'))
