# -*- coding: utf-8 -*-

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

    def tearDown(self):
        pass
