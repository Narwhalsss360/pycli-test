'''
    Example CLI Program
'''

import os
import math
from typing import Any, Optional
from traceback import print_exc
from pycli import CLI, Verb, Command
from pycli.command import cmd
from pycli.errors import CLIError

DEFAULT_TABWIDTH = 4

def parse_bool(entry: str) -> bool:
    '''
        Custom bool parser
        Default bool(str) just checkes where str is empty
    '''

    entry = entry.lower()
    falsy, truthy = ('no',  'false',    'negative', 'deny'), \
                    ('yes', 'true',     'positive', 'allow')
    if entry in falsy:
        return False
    elif entry in truthy:
        return True

    raise ValueError(f'Parsing bool must be {falsy=} or {truthy=}')

cli = CLI('CLI App', '>', \
        arg_parsers={bool: parse_bool}, \
        ignore_case=True, \
        env_vars={
            'username': None,
            'age': None,
            'user-items': {},
            'tabwidth': DEFAULT_TABWIDTH
            } \
        )

setter = Verb(cli, 'set')
getter = Verb(cli, 'get')

def expanded_tab() -> str:
    '''Expand tabwidth "\t"->"    "'''

    if 'tabwidth' not in cli.env_vars:
        cli.env_vars['tabwidth'] = DEFAULT_TABWIDTH
    return ' ' * cli.env_vars['tabwidth']

@cli.command(matches=['help'])
def uhelp(command_name: Optional[str] = None, full: Optional[bool] = False) -> str:
    '''
        Show help for `command_name` if supplied, show help for all of not supplied
    '''

    help_cmd = cmd(cli, uhelp)

    if command_name is None:
        help_cmd.options['title'] = 'Help'
        help_cmd.options['delimiter'] = '\n'
        desc = ''
        last = len(cli.commands()) - 1
        for i, command in enumerate(cli.commands()):
            desc += f'\t{command.detail}'
            if full:
                desc += f' | {"" if command.function.__doc__ is None else command.function.__doc__}'
            if i != last:
                desc += '\n'
        return desc

    command = cli.match_command(command_name)

    help_cmd.options['title'] = 'Help for'
    help_cmd.options['delimiter'] = ' '

    return command.detail + \
        (f' | {"" if command.function.__doc__ is None else command.function.__doc__}' if full else '')

@cli.command(options={'ignore-value': True})
def clear() -> None:
    '''Clear the output window'''

    os.system('cls' if os.name == 'nt' else 'clear')

@cli.command(matches=('quit', 'exit', 'q'), options={'ignore-value': True})
def uquit() -> None:
    ''' Exit the program'''

    cli.stop()

@setter.noun()
def setname(name: str) -> str:
    '''Set environment variable name'''

    cli.env_vars['username'] = name
    if name:
        cli.title = f'{name}@CLI App'
    else:
        cli.title = 'CLI App'
    return name

@setter.noun()
def setage(age: int) -> int:
    '''Set environment variable age'''

    cli.env_vars['age'] = age
    return age

@setter.noun()
def setitem(key: str, value: Optional[str] = None) -> str:
    '''Set key-value pair'''

    if key in cli.env_vars:
        cli.env_vars[key] = value
        return f'Overwritten as {key}:{value}'
    cli.env_vars[key] = value
    return f'{key}:{value}'

@setter.noun()
def settabwidth(width: int) -> str | None:
    '''Set environment variable tabwidth'''

    if width <= 0:
        return 'Error, tabwidth must be greater than 0'
    cli.env_vars['tabwidth'] = 4

@getter.noun()
def getname() -> str:
    '''Get environment variable name'''

    if 'username' not in cli.env_vars:
        return ''
    if cli.env_vars['username'] is None:
        return ''
    return cli.env_vars['username']

@getter.noun()
def getage() -> int:
    '''Get environment variable age'''

    if 'age' not in cli.env_vars:
        return ''
    if cli.env_vars['age'] is None:
        return ''
    return cli.env_vars['age']

@getter.noun()
def getitem(key: Optional[str] = None) -> str:
    '''Get key-value pair, all if key is None'''

    if 'user-items' not in cli.env_vars:
        return ''

    if key is None:
        message = '\n'
        for key, value in cli.env_vars['user-items']:
            message += f'\t{key}:{value}'
        return message

    if key not in cli.env_vars:
        return f'Key {key} does not exist'

    return cli.env_vars[key]

@getter.noun()
def gettabwidth() -> int:
    '''get environment variable tabwidth'''

    if 'tabwidth' not in cli.env_vars:
        cli.env_vars['tabwidth'] = DEFAULT_TABWIDTH

    return cli.env_vars['tabwidth']

@cli.command(matches=['printfile', 'print'], options={'delimiter': ':\n'})
def printfile(path: str, line_no: bool = False, encoding: Optional[str] = None) -> str:
    '''
        Show contents of a file
        line_no -> show line numbers
        encoding -> Text encoding
    '''

    print_cmd = cmd(cli, printfile)
    print_cmd.options.pop('title', None)

    if not os.path.isfile(path):
        raise FileNotFoundError(f'File {path} does not exist')

    print_cmd.options['title'] = os.path.basename(path)

    lines: list[str] = []
    with open(path, 'r', encoding=encoding) as f:
        lines = f.readlines()

    max_digit_count = math.ceil(math.log10(len(lines)))

    def line_number(idx: int) -> str:
        if not line_no:
            return ''
        return f'{format(idx, f"0{max_digit_count}")}|'

    output = ''

    for index, line in enumerate(lines):
        output += f'{line_number(index)}{line}'

    return output

@cli.command()
def route(*args) -> int:
    '''
        Route args to system.
    '''

    route_cmd = cmd(cli, route)

    if args:
        route_cmd.options['title'] = args[0]
    else:
        route_cmd.options['title'] = 'route'

    system_command = ''
    for i, arg in enumerate(args):
        system_command += arg
        if i != len(args) - 1:
            system_command += ' '
    return os.system(system_command)

@cli.command(options={'ignore-value': True})
def echo(string: str, second: Optional[str] = None, flat: bool = False, *args, **kwargs) -> None:
    '''
        Echo arguments
    '''

    print(f'{string=}')
    if second is not None:
        print(f'{second=}')

    if flat:
        if args:
            print(f'{args=}')
        if kwargs:
            print(f'{kwargs=}')
    else:
        for i, arg in enumerate(args):
            print(f'{i}:{arg}')
        for key, value in kwargs.items():
            print(f'{key}:{value}')

def exception_handler(exception: Exception) -> None:
    '''Invoked when an exception is raised in run()'''

    if issubclass(exception.__class__, CLIError):
        if cli.invoking() is None:
            print(f'! An error occured: {exception}')
        else:
            print(f'! An error occured running command {cli.invoking().matches[0]}: {exception}')
        if exception.__cause__ is not None:
            print(f'! Cause: {exception.__cause__}')
    else:
        print(f'Unkown exception was raised: {exception}')
        print_exc()

def return_value_handler(command: Command, value: Any) -> None:
    '''Handles command return values'''

    if 'ignore-value' in command.options and command.options['ignore-value']:
        return

    title = command.matches[0]
    if 'title' in command.options:
        title = command.options['title']

    delimiter = '->'
    if 'delimiter' in command.options:
        delimiter = command.options['delimiter']

    if value is None:
        print(f'{title}{delimiter}Done!')
        return

    print(f'{title}{delimiter}{value}')

if __name__ == '__main__':
    cli.run(exception_handler, return_value_handler)
