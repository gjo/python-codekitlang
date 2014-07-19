===========
CodeKitLang
===========

A `CodeKit Language`_ compiler based on Python.

There is the `Reference implementation`_ written by Objective-C.

.. _CodeKit Language: http://incident57.com/codekit/kit.php
.. _Reference implementation: https://github.com/bdkjones/Kit


Install
=======

From PyPI::

  pip install CodeKitLang

From source::

  python setup.py install


Running Compiler
================

Run ``pykitlangc`` or ``python -m codekitlang.command``::

  usage: pykitlangc [-h] [-f DIR] [--missing-file-behavior BEHAVIOR]
                    [--missing-variable-behavior BEHAVIOR]
                    SRC DEST

  CodeKit Language Compiler.

  positional arguments:
    SRC                   input file
    DEST                  output file

  optional arguments:
    -h, --help            show this help message and exit
    -f DIR, --framework-paths DIR
                          path for lookup include file (allow multiple defs)
    --missing-file-behavior BEHAVIOR
                          one of ignore, logonly, exception (default: logonly)
    --missing-variable-behavior BEHAVIOR
                          one of ignore, logonly, exception (default: ignore)


Running Tests
=============

From the top level directory run ``python setup.py test`` or run ``py.test``.


TODO
====

Under features are planed, but not implement yet.

- Directory recursive compile.
- Watchdog integration.
- Encoding Detection.
- Python3 support.


License
=======

CodeKitLang is offered under BSD License.
