# -*- coding: utf-8 -*-

import difflib
import os
import shutil
import tempfile
import unittest
import mock
import testfixtures


class ExceptionStringTestCase(unittest.TestCase):

    def test_compile_error(self):
        from ..compiler import CompileError
        ex = CompileError()
        ex.to_message()

    def test_cyclic_inclusion_error(self):
        from ..compiler import CyclicInclusionError
        ex = CyclicInclusionError('A', ('B', 'C', 'D'))
        self.assertEqual(
            ex.to_message(),
            'Compile Error: file "A" is included already '
            'from "D" from "C" from "B"'
        )


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

        def touch(x):
            open(fn, 'wb').write(x)

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
        from ..compiler import Fragment
        ret = self.func('')
        self.assertEqual([Fragment(0, 1, 1, 'NOOP', '')], ret)

    def test_noop_2(self):
        from ..compiler import Fragment
        ret = self.func('not comments')
        self.assertEqual([Fragment(0, 1, 1, 'NOOP', 'not comments')], ret)

    def test_noop_3(self):
        from ..compiler import Fragment
        ret = self.func('not <!-- dummy comment --> symbol')
        self.assertEqual(
            [Fragment(0, 1, 1, 'NOOP', 'not <!-- dummy comment --> symbol')],
            ret
        )

    def test_jump_1(self):
        from ..compiler import Fragment
        ret = self.func('pre <!--@include aaa--> post')
        self.assertEqual([Fragment(0, 1, 1, 'NOOP', 'pre '),
                          Fragment(4, 1, 5, 'JUMP', 'aaa'),
                          Fragment(23, 1, 24, 'NOOP', ' post')], ret)

    def test_jump_2(self):
        from ..compiler import Fragment
        ret = self.func('pre <!-- @import "b b b" --> post')
        self.assertEqual([Fragment(0, 1, 1, 'NOOP', 'pre '),
                          Fragment(4, 1, 5, 'JUMP', 'b b b'),
                          Fragment(28, 1, 29, 'NOOP', ' post')], ret)

    def test_jump_3(self):
        from ..compiler import Fragment
        ret = self.func("pre <!-- @INCLUDE ccc, 'd d d' --> post")
        self.assertEqual([Fragment(0, 1, 1, 'NOOP', 'pre '),
                          Fragment(4, 1, 5, 'JUMP', 'ccc'),
                          Fragment(4, 1, 5, 'JUMP', 'd d d'),
                          Fragment(34, 1, 35, 'NOOP', ' post')], ret)

    def test_jump_4(self):
        from ..compiler import Fragment
        ret = self.func("""pre <!--
        @INCLUDE
        eee,
        fff
        --> post""")
        self.assertEqual([Fragment(0, 1, 1, 'NOOP', 'pre '),
                          Fragment(4, 1, 5, 'JUMP', 'eee'),
                          Fragment(4, 1, 5, 'JUMP', 'fff'),
                          Fragment(62, 5, 12, 'NOOP', ' post')], ret)

    def test_load_1(self):
        from ..compiler import Fragment
        ret = self.func('pre <!--@var1--> post')
        self.assertEqual([Fragment(0, 1, 1, 'NOOP', 'pre '),
                          Fragment(4, 1, 5, 'LOAD', 'var1'),
                          Fragment(16, 1, 17, 'NOOP', ' post')], ret)

    def test_load_2(self):
        from ..compiler import Fragment
        ret = self.func('pre <!-- $VAR2 --> post')
        self.assertEqual([Fragment(0, 1, 1, 'NOOP', 'pre '),
                          Fragment(4, 1, 5, 'LOAD', 'VAR2'),
                          Fragment(18, 1, 19, 'NOOP', ' post')], ret)

    def test_load_3(self):
        from ..compiler import Fragment
        source = '<!--$cssPath-->main.css">' \
                 '<!--[if lt IE 7]><p>NOOOO</p><![endif]-->'
        remainder = 'main.css"><!--[if lt IE 7]><p>NOOOO</p><![endif]-->'
        ret = self.func(source)
        self.assertEqual([Fragment(0, 1, 1, 'LOAD', 'cssPath'),
                          Fragment(15, 1, 16, 'NOOP', remainder)], ret)

    def test_stor_1(self):
        from ..compiler import Fragment
        ret = self.func('pre <!--@var_A val1--> post')
        self.assertEqual([Fragment(0, 1, 1, 'NOOP', 'pre '),
                          Fragment(4, 1, 5, 'STOR', ('var_A', 'val1')),
                          Fragment(22, 1, 23, 'NOOP', ' post')], ret)

    def test_stor_2(self):
        from ..compiler import Fragment
        ret = self.func('pre <!-- @var_B:val2 --> post')
        self.assertEqual([Fragment(0, 1, 1, 'NOOP', 'pre '),
                          Fragment(4, 1, 5, 'STOR', ('var_B', 'val2')),
                          Fragment(24, 1, 25, 'NOOP', ' post')], ret)

    def test_stor_3(self):
        from ..compiler import Fragment
        ret = self.func('pre <!-- $var_C = v a l 3 --> post')
        self.assertEqual([Fragment(0, 1, 1, 'NOOP', 'pre '),
                          Fragment(4, 1, 5, 'STOR', ('var_C', 'v a l 3')),
                          Fragment(29, 1, 30, 'NOOP', ' post')], ret)

    def test_stor_4(self):
        from ..compiler import Fragment
        ret = self.func("""pre <!--
        $var_D
very
long
value
--> post""")
        self.assertEqual([
            Fragment(0, 1, 1, 'NOOP', 'pre '),
            Fragment(4, 1, 5, 'STOR', ('var_D', 'very\nlong\nvalue')),
            Fragment(43, 6, 4, 'NOOP', ' post'),
        ], ret)


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
        from ..compiler import Fragment
        self.assertParsed('file1.html')
        self.assertEqual(
            self.obj.parsed_caches[
                os.path.join(self.basepath, 'file1.html')
            ]['data'],
            [Fragment(0, 1, 1, 'NOOP', 'file1.html\n')]
        )

    def test_2(self):
        from ..compiler import Fragment
        self.assertParsed('parse_file_test2.html')
        self.assertEqual(
            self.obj.parsed_caches[
                os.path.join(self.basepath, 'parse_file_test2.html')
            ]['data'],
            [Fragment(0, 1, 1, 'NOOP',
                      'AAA\n' +
                      '<!--$aaa AAA-->\n' +
                      '<!--@include parse_file_test3-->\n' +
                      '<!--$aaa-->\n' +
                      'BBB\n')]
        )

    def test_3(self):
        from ..compiler import Fragment
        self.assertParsed('parse_file_test3.kit')
        self.assertEqual(
            self.obj.parsed_caches[
                os.path.join(self.basepath, 'parse_file_test2.html')
            ]['data'],
            [Fragment(0, 1, 1, 'NOOP',
                      'AAA\n' +
                      '<!--$aaa AAA-->\n' +
                      '<!--@include parse_file_test3-->\n' +
                      '<!--$aaa-->\n' +
                      'BBB\n')]
        )
        self.assertEqual(
            self.obj.parsed_caches[
                os.path.join(self.basepath, 'parse_file_test3.kit')
            ]['data'],
            [Fragment(0, 1, 1, 'NOOP', 'AAA\n'),
             Fragment(4, 2, 1, 'STOR', ('aaa', 'AAA')),
             Fragment(19, 2, 16, 'NOOP', '\n'),
             Fragment(20, 3, 1, 'JUMP',
                      os.path.join(self.dp, 'b', 'parse_file_test2.html')),
             Fragment(57, 3, 38, 'NOOP', '\n'),
             Fragment(58, 4, 1, 'LOAD', 'aaa'),
             Fragment(69, 4, 12, 'NOOP', '\nBBB\n')]
        )

    @testfixtures.log_capture()
    def test_filenotfound_logonly(self, l):
        """
        @type l: testfixtures.LogCapture
        """
        self.assertParsed('parse_file_missing_file.kit')
        l.check(
            ('codekitlang.compiler', 'WARNING',
             'Compile Error: file "None" does not found'),
        )

    def test_filenotfound_exception(self):
        from ..compiler import FileNotFoundError
        self.obj.missing_file_behavior = 'exception'
        filepath = os.path.join(self.basepath, 'parse_file_missing_file.kit')
        self.assertRaises(FileNotFoundError, self.func, filepath)


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

    @testfixtures.log_capture()
    def test_missing_var_logonly(self, l):
        """
        @type l: testfixtures.LogCapture
        """
        self.obj.missing_variable_behavior = 'logonly'
        self.assertGenerateToStr('generate_to_str_missing_var.kit', """AAA

BBB
""")
        f = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                         'data', 'b', 'generate_to_str_missing_var.kit')
        l.check(
            ('codekitlang.compiler', 'WARNING',
             'Compile Error: variable "aaa" does not found on "{}:2:1"'
             .format(f)),
        )

    def test_missing_var_exception(self):
        from ..compiler import VariableNotFoundError
        self.obj.missing_variable_behavior = 'exception'
        filepath = os.path.join(self.basepath,
                                'generate_to_str_missing_var.kit')
        self.assertRaises(VariableNotFoundError, self.func, filepath)

    def test_cyclic_inclusion1(self):
        from ..compiler import CyclicInclusionError
        filepath = os.path.join(self.basepath,
                                'generate_to_str_cyclic_inclusion1.kit')
        self.assertRaises(CyclicInclusionError, self.func, filepath)

    def test_cyclic_inclusion2(self):
        from ..compiler import CyclicInclusionError
        filepath = os.path.join(self.basepath,
                                'generate_to_str_cyclic_inclusion2a.kit')
        self.assertRaises(CyclicInclusionError, self.func, filepath)


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

        self.assertGenerateToFile('parse_unicode_result.html',
                                  'parse_unicode.kit')
