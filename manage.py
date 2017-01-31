import importlib
import inspect
import os

from flask_script.commands import Command
from flask_script import Manager

from bijou.application import get_app

app = get_app()


def find_commands():
    '''Pick up any Manager or Command classes from bijou.commands package.'''

    def is_command_or_manager_class(m):
        if inspect.isclass(m):
            return (m != Command and issubclass(m, Command)) or (m != Manager and issubclass(m, Manager))
        else:
            return False

    commands_dir = 'bijou/commands'
    for name in os.listdir(commands_dir):
        if name.endswith('.py'):
            command_name = name.replace('.py', '')
            command_module = importlib.import_module('bijou.commands.{}'.format(command_name))

            # Manager is prefered over Command(s) because Manager usually combines them.
            commands = []
            manager = None
            for _, cls in inspect.getmembers(command_module, is_command_or_manager_class):
                if issubclass(cls, Manager):
                    manager = cls(app)
                else:
                    commands.append(cls)

            if manager:
                yield command_name, manager
            elif commands:
                if len(commands) > 1:
                    raise Exception('More than one Command discovered in {}'.format(command_module))
                yield command_name, commands[0]


if __name__ == '__main__':
    manager = Manager(app)

    for command_name, command_class in find_commands():
        manager.add_command(command_name, command_class)

    manager.run()
