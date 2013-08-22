# -*- coding: utf-8 -*-

import os
import shutil
import tempfile
import unittest


class ParseStringTestCase(unittest.TestCase):

    def setUp(self):
        from ..compiler import parse_string
        self.func = parse_string

    def test_noop_1(self):
        ret = self.func('')
        self.assertEqual([('NOOP', '')], ret)

    def test_noop_2(self):
        ret = self.func('not comments')
        self.assertEqual([('NOOP', 'not comments')], ret)

    def test_noop_3(self):
        ret = self.func('not <!-- dummy comment --> symbol')
        self.assertEqual([('NOOP', 'not <!-- dummy comment --> symbol')], ret)

    def test_jump_1(self):
        ret = self.func('pre <!--@include aaa--> post')
        self.assertEqual([('NOOP', 'pre '),
                          ('JUMP', 'aaa'),
                          ('NOOP', ' post')], ret)

    def test_jump_2(self):
        ret = self.func('pre <!-- @import "b b b" --> post')
        self.assertEqual([('NOOP', 'pre '),
                          ('JUMP', 'b b b'),
                          ('NOOP', ' post')], ret)

    def test_jump_3(self):
        ret = self.func("pre <!-- @INCLUDE ccc, 'd d d' --> post")
        self.assertEqual([('NOOP', 'pre '),
                          ('JUMP', 'ccc'),
                          ('JUMP', 'd d d'),
                          ('NOOP', ' post')], ret)

    def test_jump_4(self):
        ret = self.func("""pre <!--
        @INCLUDE
        eee,
        fff
        --> post""")
        self.assertEqual([('NOOP', 'pre '),
                          ('JUMP', 'eee'),
                          ('JUMP', 'fff'),
                          ('NOOP', ' post')], ret)

    def test_load_1(self):
        ret = self.func('pre <!--@var1--> post')
        self.assertEqual([('NOOP', 'pre '),
                          ('LOAD', 'var1'),
                          ('NOOP', ' post')], ret)

    def test_load_2(self):
        ret = self.func('pre <!-- $VAR2 --> post')
        self.assertEqual([('NOOP', 'pre '),
                          ('LOAD', 'VAR2'),
                          ('NOOP', ' post')], ret)

    def test_stor_1(self):
        ret = self.func('pre <!--@var_A val1--> post')
        self.assertEqual([('NOOP', 'pre '),
                          ('STOR', ('var_A', 'val1')),
                          ('NOOP', ' post')], ret)

    def test_stor_2(self):
        ret = self.func('pre <!-- @var_B:val2 --> post')
        self.assertEqual([('NOOP', 'pre '),
                          ('STOR', ('var_B', 'val2')),
                          ('NOOP', ' post')], ret)

    def test_stor_3(self):
        ret = self.func('pre <!-- $var_C = v a l 3 --> post')
        self.assertEqual([('NOOP', 'pre '),
                          ('STOR', ('var_C', 'v a l 3')),
                          ('NOOP', ' post')], ret)

    def test_stor_4(self):
        ret = self.func("""pre <!--
        $var_D
very
long
value
        --> post""")
        self.assertEqual([('NOOP', 'pre '),
                          ('STOR', ('var_D', 'very\nlong\nvalue')),
                          ('NOOP', ' post')], ret)


class GetFilePathTestCase(unittest.TestCase):

    def setUp(self):
        from ..compiler import get_filepath
        self.func = get_filepath
        self.tempdir = tempfile.mkdtemp()
        os.makedirs(os.path.join(self.tempdir, 'base', 'subdir'))
        os.makedirs(os.path.join(self.tempdir, 'frameworks', '1', 'subdir'))
        os.makedirs(os.path.join(self.tempdir, 'frameworks', '2'))

        def touch(*p):
            open(os.path.join(self.tempdir, *p), 'wb').write('')

        touch('base', 'file1.html')
        touch('base', 'file2.kit')
        touch('base', '_file3.kit')
        touch('base', 'subdir', 'file4.html')
        touch('base', 'subdir', 'file5.kit')
        touch('base', 'subdir', '_file6.kit')
        touch('frameworks', '1', 'file7.html')
        touch('frameworks', '1', 'file8.kit')
        touch('frameworks', '1', '_file9.kit')
        touch('frameworks', '1', 'subdir', 'file10.html')
        touch('frameworks', '1', 'subdir', 'file11.kit')
        touch('frameworks', '1', 'subdir', '_file12.kit')
        touch('frameworks', '2', 'file13.html')
        touch('frameworks', '2', 'file14.kit')
        touch('frameworks', '2', '_file15.kit')
        return

    def tearDown(self):
        if hasattr(self, 'tempdir') and os.path.exists(self.tempdir):
            shutil.rmtree(self.tempdir, ignore_errors=True)

    def assertFound(self, src, dest, msg=None):
        self.assertEqual(
            self.func(
                src,
                os.path.join(self.tempdir, 'base'),
                (os.path.join(self.tempdir, 'frameworks', '1'),
                 os.path.join(self.tempdir, 'frameworks', '2')),
            ),
            os.path.join(self.tempdir, *dest),
            msg=msg,
        )

    def assertNotFound(self, src, msg=None):
        self.assertIsNone(
            self.func(
                src,
                os.path.join(self.tempdir, 'base'),
                (os.path.join(self.tempdir, 'frameworks', '1'),
                 os.path.join(self.tempdir, 'frameworks', '2')),
            ),
            msg=msg,
        )

    def test(self):
        self.assertFound('file1.html', ('base', 'file1.html'))
        self.assertNotFound('file1')
        self.assertNotFound('file2.html')
        self.assertFound('file2', ('base', 'file2.kit'))
        self.assertFound('file2.kit', ('base', 'file2.kit'))
        self.assertFound('file3', ('base', '_file3.kit'))
        self.assertFound('file3.kit', ('base', '_file3.kit'))
        self.assertFound('_file3', ('base', '_file3.kit'))
        self.assertFound('_file3.kit', ('base', '_file3.kit'))

        self.assertFound('subdir/file4.html', ('base', 'subdir', 'file4.html'))
        self.assertNotFound('subdir/file4')
        self.assertNotFound('subdir/file5.html')
        self.assertFound('subdir/file5', ('base', 'subdir', 'file5.kit'))
        self.assertFound('subdir/file5.kit', ('base', 'subdir', 'file5.kit'))
        self.assertFound('subdir/file6', ('base', 'subdir', '_file6.kit'))
        self.assertFound('subdir/file6.kit', ('base', 'subdir', '_file6.kit'))
        self.assertFound('subdir/_file6', ('base', 'subdir', '_file6.kit'))
        self.assertFound('subdir/_file6.kit', ('base', 'subdir', '_file6.kit'))

        self.assertNotFound('file7')
        self.assertNotFound('file7.html')
        self.assertNotFound('file8.html')
        self.assertFound('file8', ('frameworks', '1', 'file8.kit'))
        self.assertFound('file8.kit', ('frameworks', '1', 'file8.kit'))
        self.assertFound('file9', ('frameworks', '1', '_file9.kit'))
        self.assertFound('file9.kit', ('frameworks', '1', '_file9.kit'))
        self.assertFound('_file9', ('frameworks', '1', '_file9.kit'))
        self.assertFound('_file9.kit', ('frameworks', '1', '_file9.kit'))

        self.assertNotFound('subdir/file10')
        self.assertNotFound('subdir/file10.html')
        self.assertNotFound('subdir/file11.html')
        self.assertFound('subdir/file11',
                         ('frameworks', '1', 'subdir', 'file11.kit'))
        self.assertFound('subdir/file11.kit',
                         ('frameworks', '1', 'subdir', 'file11.kit'))
        self.assertFound('subdir/file12',
                         ('frameworks', '1', 'subdir', '_file12.kit'))
        self.assertFound('subdir/file12.kit',
                         ('frameworks', '1', 'subdir', '_file12.kit'))
        self.assertFound('subdir/_file12',
                         ('frameworks', '1', 'subdir', '_file12.kit'))
        self.assertFound('subdir/_file12.kit',
                         ('frameworks', '1', 'subdir', '_file12.kit'))

        self.assertNotFound('file13')
        self.assertNotFound('file13.html')
        self.assertNotFound('file14.html')
        self.assertFound('file14', ('frameworks', '2', 'file14.kit'))
        self.assertFound('file14.kit', ('frameworks', '2', 'file14.kit'))
        self.assertFound('file15', ('frameworks', '2', '_file15.kit'))
        self.assertFound('file15.kit', ('frameworks', '2', '_file15.kit'))
        self.assertFound('_file15', ('frameworks', '2', '_file15.kit'))
        self.assertFound('_file15.kit', ('frameworks', '2', '_file15.kit'))
