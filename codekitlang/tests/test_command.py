# -*- coding: utf-8 -*-

import difflib
import os
import shutil
import tempfile
import unittest
import mock


class CommandTestCase(unittest.TestCase):

    def setUp(self):
        self.dp = os.path.join(os.path.dirname(__file__), 'data')
        self.basepath = os.path.join(self.dp, 'b')
        self.destpath = os.path.join(self.dp, 'd')
        self.framework_paths = (
            os.path.join(self.dp, 'f1'),
            os.path.join(self.dp, 'f2'),
        )
        self.tempdir = tempfile.mkdtemp()

    def tearDown(self):
        if hasattr(self, 'tempdir') and os.path.exists(self.tempdir):
            shutil.rmtree(self.tempdir, ignore_errors=True)

    def test_no_argv(self):
        with mock.patch('sys.argv', new=['PROG']):
            from .. import command
            self.assertRaises(SystemExit, command.main)

    @mock.patch('codekitlang.compiler.Compiler.generate_to_file')
    def test_no_option(self, mocked_generate_to_file):
        with mock.patch('sys.argv', new=['PROG', 'SRC', 'DEST']):
            from .. import command
            command.main()
            mocked_generate_to_file.assert_called_with('DEST', 'SRC')

    def test(self):
        argv = ['PROG']
        for p in self.framework_paths:
            argv.extend(['-f', p])
        argv.extend([os.path.join(self.basepath, 'parse_file_test3.kit'),
                     os.path.join(self.tempdir, 'parse_file_test3.html')])
        with mock.patch('sys.argv', new=argv):
            from .. import command
            command.main()

        with open(os.path.join(self.destpath, 'dd', 'parse_file_test3.html'),
                  'rb') as fp:
            forecast = fp.read()
        with open(os.path.join(self.tempdir, 'parse_file_test3.html'),
                  'rb') as fp:
            actual = fp.read()
        self.assertListEqual(list(difflib.unified_diff(forecast, actual)), [])
