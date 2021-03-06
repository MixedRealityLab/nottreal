#!/usr/bin/env python

from nottreal.utils.log import Logger
from nottreal.utils.init import ArgparseUtils
from nottreal.app import App

from argparse import ArgumentParser

import glob
import os
import sys

modules = glob.glob(os.path.join(os.path.dirname(__file__), '*.py'))
__all__ = [os.path.basename(f)[:-3]
           for f in modules if not f.endswith('__init__.py')]


def main():
    """
    Entry point for the application. Checks the command line arguments,
    validates the configuration, and starts the GUI application.
    """
    # n.b. apps frozen with python3.8 get this far when
    # double clicked (CLI opening is ok)

    parser = ArgumentParser(prog='NottReal')
    parser.add_argument(
        '-l',
        '--log',
        choices={'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'},
        default='INFO',
        help='Minimum level of log output.')
    parser.add_argument(
        '-c',
        '--config_dir',
        default='cfg.nrc',
        type=ArgparseUtils.dir_contains_config,
        help='Directory containing the configuration files')
    parser.add_argument(
        '-d',
        '--output_dir',
        default=None,
        type=ArgparseUtils.dir_is_writeable,
        help='Directory to dump logs from spoken text (disabled by default)')
    parser.add_argument(
        '-r',
        '--recognition',
        default=None,
        help='Speech-to-text recognition system to use')
    parser.add_argument(
        '-v',
        '--voice',
        default=None,
        help='Voice synthesis library to use')
    parser.add_argument(
        '-o',
        '--output_win',
        default='disabled',
        help='Show an output window on opening')
    parser.add_argument(
        '-ns',
        '--nostate',
        default=False,
        action='store_true',
        help='Disable automatic state saving in config directory')
    parser.add_argument(
        '-dev',
        '--dev',
        action='store_true',
        help='Enable developer mode/disable catching of errors')
    args = parser.parse_args()

    Logger.init(getattr(Logger, args.log))
    Logger.info(__name__, "Hello, World")
    Logger.info(__name__, str(sys.argv))

    ArgparseUtils.init_darwin()

    App(args)

    Logger.info(__name__, "Goodbye, World")
    sys.exit(0)


if __name__ == '__main__':
    main()
