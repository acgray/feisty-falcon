import argparse
import importlib
import os
import re
import sys

import feisty
import feisty.generate


class CommandLineError(Exception):
    def __init__(self, error):
        self.error = error


def _feisty_command_line():
    parser = argparse.ArgumentParser()
    parser.add_argument('api_object')
    parser.add_argument('--debug', type=bool)

    args = parser.parse_args()

    try:
        m = re.match(
            r'^([a-zA-Z0-9_.]+):([a-zA-Z0-9_.]+)',
            args.api_object)
        _mod, _sym = m.groups()
    except (ValueError, AttributeError):
        raise CommandLineError(
            'Please specify the location of your Falcon API '
            'object in the form some.module:obj')
    try:
        mod = importlib.import_module(_mod)
        api = getattr(mod, _sym)
    except (ImportError, AttributeError):
        raise CommandLineError(
            'Could not locate the API object {}'.format(args.api_object))

    try:
        spec = feisty.generate.generate_schema(api)
        sys.stdout.write(spec.to_yaml())
        sys.exit(0)
    except ValueError as e:
        raise CommandLineError(e.args[0])


def main():
    try:
        _feisty_command_line()
    except CommandLineError as e:
        if os.environ.get('DEBUG'):
            raise
        else:
            sys.stderr.write(e.error + '\n')
            sys.exit(1)
