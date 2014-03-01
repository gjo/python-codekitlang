# -*- coding: utf-8 -*-

import argparse
from . import compiler


def main():
    parser = argparse.ArgumentParser(description='CodeKit Language Compiler.')
    parser.add_argument('src', nargs=1, metavar='SOURCE')
    parser.add_argument('dest', nargs=1, metavar='DEST')
    parser.add_argument('--framework-paths', '-f', action='append',
                        metavar='DIR')
    namespace = parser.parse_args()
    options = vars(namespace)
    src = options.pop('src')[0]
    dest = options.pop('dest')[0]
    compiler_ = compiler.Compiler(**options)
    compiler_.generate_to_file(dest, src)

if __name__ == '__main__':  # pragma:nocover
    main()
