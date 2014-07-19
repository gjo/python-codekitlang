# -*- coding: utf-8 -*-

from __future__ import print_function

import argparse
import logging
import sys
from . import compiler


def _(s):
    return s


def main():
    parser = argparse.ArgumentParser(
        prog='pykitlangc',
        description=_('CodeKit Language Compiler.'),
    )
    parser.add_argument('src', nargs=1, metavar='SRC', help=_('input file'))
    parser.add_argument('dest', nargs=1, metavar='DEST', help=_('output file'))
    parser.add_argument(
        '-f', '--framework-paths', metavar='DIR', action='append',
        help=_('path for lookup include file (allow multiple defs)'),
    )
    parser.add_argument(
        '--missing-file-behavior', metavar='BEHAVIOR', default='logonly',
        choices=('ignore', 'logonly', 'exception'),
        help=_('one of ignore, logonly, exception (default: logonly)'),
    )
    parser.add_argument(
        '--missing-variable-behavior', metavar='BEHAVIOR', default='ignore',
        choices=('ignore', 'logonly', 'exception'),
        help=_('one of ignore, logonly, exception (default: ignore)'),
    )
    namespace = parser.parse_args()
    options = vars(namespace)
    src = options.pop('src')
    dest = options.pop('dest')
    logger = logging.getLogger('pykitlangc')
    logger.addHandler(logging.StreamHandler())
    logger.setLevel(logging.INFO)
    options['logger'] = logger
    compiler_ = compiler.Compiler(**options)
    try:
        compiler_.generate_to_file(dest[0], src[0])
    except compiler.CompileError as e:
        print(e.to_message(), file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':  # pragma:nocover
    main()
