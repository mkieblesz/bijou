import unittest
from flask_script.commands import Command, Option

from bijou.application import get_test_app


class TestCommand(Command):
    option_list = (
        Option('-v', '--verbose', default=1, required=False),
        Option('-d', '--debug', action='store_true', default=False, required=False),
    )

    def __init__(self, *args, **kwargs):
        # this allows to pass arguments to command without specifying target
        self.capture_all_args = True

        super(TestCommand, self).__init__(*args, **kwargs)

    def run(self, *args, **kwargs):
        '''
        By default we run tests using cached responses. If they are not present or some are missing error will be
        raised.
        '''
        app = get_test_app()

        verbosity = kwargs.get('verbose')
        debug = kwargs.get('debug')

        app.config.update({
            'DEBUG': debug
        })

        if args[0]:
            testsuite = unittest.TestLoader().loadTestsFromNames(args[0])
        else:
            testsuite = unittest.TestLoader().discover('./tests/')

        unittest.TextTestRunner(verbosity=int(verbosity)).run(testsuite)
