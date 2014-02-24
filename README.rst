===========
CodeKitLang
===========

A `CodeKit Language`_ compiler based on Python.

There is the `Reference implementation`_ written by Objective-C.

.. _CodeKit Language: http://incident57.com/codekit/kit.php
.. _Reference implementation: https://github.com/bdkjones/Kit

INSTALL
=======

From PyPI::

  pip install CodeKitLang

From source::

  python setup.py install

RUNNING COMPILER
================

Run ``pykitlangc`` or ``python -m codekitlang.command``::

  usage: command.py [-h] [--framework-paths DIR] SOURCE DEST

  CodeKit Language Compiler.

  positional arguments:
    SOURCE
    DEST

  optional arguments:
    -h, --help            show this help message and exit
    --framework-paths DIR, -f DIR

RUNNING TESTS
=============

From the top level directory run ``python setup.py test`` or run ``py.test``.

TODO
====

Under features are planed, but not implement yet.

- User friendly error messages.
- Detect cyclic inclusion.
- Handle options for files not found.
- Handle options for variables not found.
- Directory recursive compile.
- Watchdog integration.
- Encoding Detection.
- Python3 support.

License
=======

CodeKitLang is offered under BSD License.
