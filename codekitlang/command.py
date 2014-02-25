# -*- coding: utf-8 -*-

import argparse
from . import compiler


def main():
    parser = argparse.ArgumentParser(description='CodeKit Language Compiler.')
    parser.add_argument('src', nargs=1, metavar='SOURCE')
    parser.add_argument('dest', nargs=1, metavar='DEST')
    parser.add_argument('--framework-paths', '-f', action='append',
                        metavar='DIR')
    parser.add_argument('--missing-file', choices=['ignore', 'warn', 'error'],
                        default='warn', metavar='BEHAVIOR')
    parser.add_argument('--missing-variable',
                        choices=['ignore', 'warn', 'error'],
                        default='ignore', metavar='BEHAVIOR')
    namespace = parser.parse_args()
    compiler_ = compiler.Compiler(
        framework_paths=namespace.framework_paths,
        missing_file=namespace.missing_file,
        missing_variable=namespace.missing_variable,
    )
    compiler_.generate_to_file(namespace.dest[0], namespace.src[0])

if __name__ == '__main__':  # pragma:nocover
    main()
