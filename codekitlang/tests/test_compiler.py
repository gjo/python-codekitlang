# -*- coding: utf-8 -*-

import difflib
import os
import shutil
import tempfile
import unittest
import mock


class InitTestCase(unittest.TestCase):

    def test_fp_none(self):
        from ..compiler import Compiler
        obj = Compiler()
        self.assertEqual(obj.framework_paths, ())

    def test_fp_str(self):
        from ..compiler import Compiler
        obj = Compiler(framework_paths='TESTPATH')
        self.assertEqual(obj.framework_paths, ('TESTPATH',))

    def test_fp_list1(self):
        from ..compiler import Compiler
        obj = Compiler(framework_paths=['TESTPATH'])
        self.assertEqual(obj.framework_paths, ('TESTPATH',))

    def test_fp_list2(self):
        from ..compiler import Compiler
        obj = Compiler(framework_paths=['TESTPATH1', 'TESTPATH2'])
        self.assertEqual(obj.framework_paths, ('TESTPATH1', 'TESTPATH2'))


class ResolveFilePathTestCase(unittest.TestCase):

    def setUp(self):
        from ..compiler import Compiler
        self.dp = os.path.join(os.path.dirname(__file__), 'data')
        self.obj = Compiler(framework_paths=(
            os.path.join(self.dp, 'f1'),
            os.path.join(self.dp, 'f2'),
        ))
        self.func = self.obj.resolve_path

    def assertFound(self, src, dest, msg=None):
        self.assertEqual(
            self.func(src, os.path.join(self.dp, 'b')),
            os.path.realpath(os.path.join(self.dp, *dest)),
            msg=msg,
        )

    def assertNotFound(self, src, msg=None):
        self.assertIsNone(self.func(src, os.path.join(self.dp, 'b')), msg=msg)

    def test(self):
        self.assertFound('file1.html', ('b', 'file1.html'))
        self.assertNotFound('file1')
        self.assertNotFound('file2.html')
        self.assertFound('file2', ('b', 'file2.kit'))
        self.assertFound('file2.kit', ('b', 'file2.kit'))
        self.assertFound('file3', ('b', '_file3.kit'))
        self.assertFound('file3.kit', ('b', '_file3.kit'))
        self.assertFound('_file3', ('b', '_file3.kit'))
        self.assertFound('_file3.kit', ('b', '_file3.kit'))

        self.assertFound('sub/file4.html', ('b', 'sub', 'file4.html'))
        self.assertNotFound('sub/file4')
        self.assertNotFound('sub/file5.html')
        self.assertFound('sub/file5', ('b', 'sub', 'file5.kit'))
        self.assertFound('sub/file5.kit', ('b', 'sub', 'file5.kit'))
        self.assertFound('sub/file6', ('b', 'sub', '_file6.kit'))
        self.assertFound('sub/file6.kit', ('b', 'sub', '_file6.kit'))
        self.assertFound('sub/_file6', ('b', 'sub', '_file6.kit'))
        self.assertFound('sub/_file6.kit', ('b', 'sub', '_file6.kit'))

        self.assertNotFound('file7')
        self.assertNotFound('file7.html')
        self.assertNotFound('file8.html')
        self.assertFound('file8', ('f1', 'file8.kit'))
        self.assertFound('file8.kit', ('f1', 'file8.kit'))
        self.assertFound('file9', ('f1', '_file9.kit'))
        self.assertFound('file9.kit', ('f1', '_file9.kit'))
        self.assertFound('_file9', ('f1', '_file9.kit'))
        self.assertFound('_file9.kit', ('f1', '_file9.kit'))

        self.assertNotFound('sub/file10')
        self.assertNotFound('sub/file10.html')
        self.assertNotFound('sub/file11.html')
        self.assertFound('sub/file11', ('f1', 'sub', 'file11.kit'))
        self.assertFound('sub/file11.kit', ('f1', 'sub', 'file11.kit'))
        self.assertFound('sub/file12', ('f1', 'sub', '_file12.kit'))
        self.assertFound('sub/file12.kit', ('f1', 'sub', '_file12.kit'))
        self.assertFound('sub/_file12', ('f1', 'sub', '_file12.kit'))
        self.assertFound('sub/_file12.kit', ('f1', 'sub', '_file12.kit'))

        self.assertNotFound('file13')
        self.assertNotFound('file13.html')
        self.assertNotFound('file14.html')
        self.assertFound('file14', ('f2', 'file14.kit'))
        self.assertFound('file14.kit', ('f2', 'file14.kit'))
        self.assertFound('file15', ('f2', '_file15.kit'))
        self.assertFound('file15.kit', ('f2', '_file15.kit'))
        self.assertFound('_file15', ('f2', '_file15.kit'))
        self.assertFound('_file15.kit', ('f2', '_file15.kit'))


class NormalizePathTestCase(unittest.TestCase):

    def setUp(self):
        from ..compiler import Compiler
        self.obj = Compiler()
        self.func = self.obj.normalize_path

    def test_filepath_relative(self):
        self.assertEqual(self.func(filepath='hoge/fuga.txt'),
                         os.path.join(os.getcwd(), 'hoge', 'fuga.txt'))

    def test_filepath_absolute(self):
        self.assertEqual(self.func(filepath='/hoge/fuga.txt'),
                         '/hoge/fuga.txt')

    def test_filepath_traversal(self):
        self.assertEqual(self.func(filepath='/hoge/dum/../fuga.txt'),
                         '/hoge/fuga.txt')

    @mock.patch('codekitlang.compiler.Compiler.resolve_path')
    def test_filename(self, mock_resolve_path):
        mock_resolve_path.return_value = 'MOCKED'
        self.assertEqual(self.func(filename='hoge', basepath='fuga'), 'MOCKED')


class GetNewSignatureTestCase(unittest.TestCase):

    def setUp(self):
        from ..compiler import Compiler
        self.obj = Compiler()
        self.func = self.obj.get_new_signature
        self.tempdir = tempfile.mkdtemp()

    def tearDown(self):
        if hasattr(self, 'tempdir') and os.path.exists(self.tempdir):
            shutil.rmtree(self.tempdir, ignore_errors=True)

    def test(self):
        fn = os.path.join(self.tempdir, 'testfile')
        touch = lambda x: open(fn, 'wb').write(x)
        touch('')
        ret1 = self.func(fn)
        self.assertIsNotNone(ret1)
        self.obj.parsed_caches[fn] = {'signature': ret1}
        self.assertIsNone(self.func(fn))
        touch('A')
        ret2 = self.func(fn)
        self.assertIsNotNone(ret2)
        self.assertNotEqual(ret1, ret2)


class ParseStrTestCase(unittest.TestCase):

    def setUp(self):
        from ..compiler import Compiler
        self.obj = Compiler()
        self.func = self.obj.parse_str

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


class ParseFileTestCase(unittest.TestCase):

    def setUp(self):
        from ..compiler import Compiler
        self.dp = os.path.join(os.path.dirname(__file__), 'data')
        self.basepath = os.path.join(self.dp, 'b')
        self.obj = Compiler(framework_paths=(
            os.path.join(self.dp, 'f1'),
            os.path.join(self.dp, 'f2'),
        ))
        self.func = self.obj.parse_file

    def assertParsed(self, filename):
        filepath = os.path.join(self.basepath, filename)
        self.assertEqual(self.func(filepath), os.path.realpath(filepath))

    def test_1(self):
        self.assertParsed('file1.html')
        self.assertEqual(
            self.obj.parsed_caches[
                os.path.join(self.basepath, 'file1.html')
            ]['data'],
            [('NOOP', 'file1.html\n')]
        )

    def test_2(self):
        self.assertParsed('parse_file_test2.html')
        self.assertEqual(
            self.obj.parsed_caches[
                os.path.join(self.basepath, 'parse_file_test2.html')
            ]['data'],
            [('NOOP', 'AAA\n'
                      '<!--$aaa AAA-->\n'
                      '<!--@include parse_file_test3-->\n'
                      '<!--$aaa-->\n'
                      'BBB\n')]
        )

    def test_3(self):
        self.assertParsed('parse_file_test3.kit')
        self.assertEqual(
            self.obj.parsed_caches[
                os.path.join(self.basepath, 'parse_file_test2.html')
            ]['data'],
            [('NOOP', 'AAA\n'
                      '<!--$aaa AAA-->\n'
                      '<!--@include parse_file_test3-->\n'
                      '<!--$aaa-->\n'
                      'BBB\n')]
        )
        self.assertEqual(
            self.obj.parsed_caches[
                os.path.join(self.basepath, 'parse_file_test3.kit')
            ]['data'],
            [('NOOP', 'AAA\n'),
             ('STOR', ('aaa', 'AAA')),
             ('NOOP', '\n'),
             ('JUMP', os.path.join(self.dp, 'b', 'parse_file_test2.html')),
             ('NOOP', '\n'),
             ('LOAD', 'aaa'),
             ('NOOP', '\nBBB\n')]
        )


class GenerateToStrTestCase(unittest.TestCase):

    def setUp(self):
        from ..compiler import Compiler
        self.dp = os.path.join(os.path.dirname(__file__), 'data')
        self.basepath = os.path.join(self.dp, 'b')
        self.obj = Compiler(framework_paths=(
            os.path.join(self.dp, 'f1'),
            os.path.join(self.dp, 'f2'),
        ))
        self.func = self.obj.generate_to_str

    def assertGenerateToStr(self, filename, content):
        filepath = os.path.join(self.basepath, filename)
        self.assertEqual(self.func(filepath), content)

    def test_1(self):
        self.assertGenerateToStr('parse_file_test3.kit', """AAA

AAA
<!--$aaa AAA-->
<!--@include parse_file_test3-->
<!--$aaa-->
BBB

AAA
BBB
""")


class GenerateToFileTestCase(unittest.TestCase):

    def setUp(self):
        from ..compiler import Compiler
        self.dp = os.path.join(os.path.dirname(__file__), 'data')
        self.basepath = os.path.join(self.dp, 'b')
        self.destpath = os.path.join(self.dp, 'd')
        self.obj = Compiler(framework_paths=(
            os.path.join(self.dp, 'f1'),
            os.path.join(self.dp, 'f2'),
        ))
        self.func = self.obj.generate_to_file
        self.tempdir = tempfile.mkdtemp()

    def tearDown(self):
        if hasattr(self, 'tempdir') and os.path.exists(self.tempdir):
            shutil.rmtree(self.tempdir, ignore_errors=True)

    def assertGenerateToFile(self, dest, src):
        dest_write_path = os.path.join(self.tempdir, dest)
        dest_path = os.path.join(self.destpath, dest)
        src_path = os.path.join(self.basepath, src)

        self.func(dest_write_path, src_path)
        self.assertTrue(os.path.exists(dest_write_path))

        with open(dest_path, 'rb') as fp:
            forecast = fp.read()
        with open(dest_write_path, 'rb') as fp:
            actual = fp.read()
        self.assertListEqual(list(difflib.unified_diff(forecast, actual)), [])

    def test(self):
        self.assertGenerateToFile('dd/parse_file_test3.html',
                                  'parse_file_test3.kit')
