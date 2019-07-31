# -*- coding: utf-8 -*-

"""
Unit tests for the normal form detection.

Author: Gertjan van den Burg

"""

import unittest

from clevercsv.dialect import SimpleDialect
from clevercsv.normal_form import (
    is_form_1,
    is_form_2,
    is_form_3,
    is_form_4,
    is_form_5,
)


class NormalFormTestCase(unittest.TestCase):
    def test_form_1(self):
        dialect = SimpleDialect(delimiter=",", quotechar='"', escapechar="")

        self.assertTrue(is_form_1('"A","B","C"', dialect))
        self.assertTrue(is_form_1('"A","B"\n"C","D"\n', dialect))
        self.assertTrue(is_form_1('"A","","C"', dialect))

        self.assertFalse(is_form_1('"A","B"\n"A"', dialect))
        self.assertFalse(is_form_1('"A"\n"B"', dialect))
        self.assertFalse(is_form_1('"A"\n"A","B"', dialect))
        self.assertFalse(is_form_1('"A",,"C"', dialect))
        self.assertFalse(is_form_1('"A",C', dialect))
        self.assertFalse(is_form_1('"A"\n"b""A""c","B"', dialect))

    def test_form_2(self):
        dialect = SimpleDialect(delimiter=",", quotechar="", escapechar="")

        self.assertTrue(is_form_2("1,2,3", dialect))
        self.assertTrue(is_form_2("1,2,3\na,b,c\n", dialect))
        self.assertTrue(is_form_2("a@b.com,3", dialect))
        self.assertTrue(is_form_2("a,,3\n1,2,3", dialect))

        self.assertFalse(is_form_2("1,2,3\n1,2\n4,5,6", dialect))
        self.assertFalse(is_form_2("1", dialect))
        self.assertFalse(is_form_2('1,"a"', dialect))
        self.assertFalse(is_form_2("a;b,3", dialect))
        self.assertFalse(is_form_2('"a,3,3\n1,2,3', dialect))
        self.assertFalse(is_form_2('a,"",3\n1,2,3', dialect))

    def test_form_3(self):
        A = SimpleDialect(delimiter=",", quotechar="'", escapechar="")
        Q = SimpleDialect(delimiter=",", quotechar='"', escapechar="")

        self.assertTrue(is_form_3('A,B\nC,"D"', Q))
        self.assertTrue(is_form_3('A,B\nC,"d,e"', Q))

        self.assertFalse(is_form_3('A,\nC,"d,e"', Q))
        self.assertFalse(is_form_3("3;4,B\nC,D", Q))

        self.assertFalse(is_form_3('A,B\n"C",D\n', A))
        self.assertTrue(is_form_3('A,B\n"C",D\n', Q))

    def test_form_4(self):
        quoted = SimpleDialect(delimiter="", quotechar='"', escapechar="")
        unquoted = SimpleDialect(delimiter="", quotechar="", escapechar="")

        self.assertTrue(is_form_4("A\nB\nC", unquoted))
        self.assertTrue(is_form_4("1\n2\n3", unquoted))
        self.assertTrue(is_form_4("A_B\n1\n2", unquoted))
        self.assertTrue(is_form_4("A&B\n1\n2", unquoted))
        self.assertTrue(is_form_4("A&B\n-1\n2", unquoted))
        self.assertTrue(is_form_4('"A"\n"B"\n"C"\n', quoted))

        self.assertFalse(is_form_4('"A", "B"\n"B"\n"C"\n', quoted))
        self.assertFalse(is_form_4('"A","B"\n"B"\n"C"\n', quoted))
        self.assertFalse(is_form_4('"A@b"\n"B"\n"C"\n', quoted))
        self.assertFalse(is_form_4('A\n"-1"\n2', unquoted))
        self.assertFalse(is_form_4("A B\n-1 3\n2 4", unquoted))

    def test_form_5(self):
        dialect = SimpleDialect(delimiter=",", quotechar='"', escapechar="")

        self.assertTrue(is_form_5('"A,B"\n"1,2"\n"3,4"', dialect))
        self.assertTrue(is_form_5('"A,B"\n"1,"\n"2,3"', dialect))

        self.assertFalse(is_form_5("A,B\n1,2\n3,4", dialect))
        self.assertFalse(is_form_5("A,B\n1,\n2,3", dialect))
        self.assertFalse(is_form_5('"A,""B"""\n"1,"\n"2,3"', dialect))


if __name__ == "__main__":
    unittest.main()
