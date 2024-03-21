# -*- coding: utf-8 -*-

"""
Unit tests for the normal form detection.

Author: Gertjan van den Burg

"""

import unittest

from clevercsv.dialect import SimpleDialect
from clevercsv.normal_form import is_form_1
from clevercsv.normal_form import is_form_2
from clevercsv.normal_form import is_form_3
from clevercsv.normal_form import is_form_4
from clevercsv.normal_form import is_form_5


class NormalFormTestCase(unittest.TestCase):
    def test_form_1(self) -> None:
        dialect = SimpleDialect(delimiter=",", quotechar='"', escapechar="")

        self.assertTrue(is_form_1('"A","B","C"'.split("\n"), dialect))
        self.assertTrue(is_form_1('"A","B"\n"C","D"'.split("\n"), dialect))
        self.assertTrue(is_form_1('"A","","C"'.split("\n"), dialect))

        self.assertFalse(is_form_1('"A","B"\n"A"'.split("\n"), dialect))
        self.assertFalse(is_form_1('"A"\n"B"'.split("\n"), dialect))
        self.assertFalse(is_form_1('"A"\n"A","B"'.split("\n"), dialect))
        self.assertFalse(is_form_1('"A",,"C"'.split("\n"), dialect))
        self.assertFalse(is_form_1('"A",C'.split("\n"), dialect))
        self.assertFalse(is_form_1('"A"\n"b""A""c","B"'.split("\n"), dialect))

    def test_form_2(self) -> None:
        dialect = SimpleDialect(delimiter=",", quotechar="", escapechar="")

        self.assertTrue(is_form_2("1,2,3".split("\n"), dialect))
        self.assertTrue(is_form_2("1,2,3\na,b,c".split("\n"), dialect))
        self.assertTrue(is_form_2("a@b.com,3".split("\n"), dialect))
        self.assertTrue(is_form_2("a,,3\n1,2,3".split("\n"), dialect))

        self.assertFalse(is_form_2("1,2,3\n1,2\n4,5,6".split("\n"), dialect))
        self.assertFalse(is_form_2("1".split("\n"), dialect))
        self.assertFalse(is_form_2('1,"a"'.split("\n"), dialect))
        self.assertFalse(is_form_2("a;b,3".split("\n"), dialect))
        self.assertFalse(is_form_2('"a,3,3\n1,2,3'.split("\n"), dialect))
        self.assertFalse(is_form_2('a,"",3\n1,2,3'.split("\n"), dialect))

    def test_form_3(self) -> None:
        A = SimpleDialect(delimiter=",", quotechar="'", escapechar="")
        Q = SimpleDialect(delimiter=",", quotechar='"', escapechar="")

        self.assertTrue(is_form_3('A,B\nC,"D"'.split("\n"), Q))
        self.assertTrue(is_form_3('A,B\nC,"d,e"'.split("\n"), Q))

        self.assertFalse(is_form_3('A,\nC,"d,e"'.split("\n"), Q))
        self.assertFalse(is_form_3("3;4,B\nC,D".split("\n"), Q))

        self.assertFalse(is_form_3('A,B\n"C",D'.split("\n"), A))
        self.assertTrue(is_form_3('A,B\n"C",D'.split("\n"), Q))

    def test_form_4(self) -> None:
        quoted = SimpleDialect(delimiter="", quotechar='"', escapechar="")
        unquoted = SimpleDialect(delimiter="", quotechar="", escapechar="")

        self.assertTrue(is_form_4("A\nB\nC".split("\n"), unquoted))
        self.assertTrue(is_form_4("1\n2\n3".split("\n"), unquoted))
        self.assertTrue(is_form_4("A_B\n1\n2".split("\n"), unquoted))
        self.assertTrue(is_form_4("A&B\n1\n2".split("\n"), unquoted))
        self.assertTrue(is_form_4("A&B\n-1\n2".split("\n"), unquoted))
        self.assertTrue(is_form_4('"A"\n"B"\n"C"'.split("\n"), quoted))

        self.assertFalse(is_form_4('"A", "B"\n"B"\n"C"'.split("\n"), quoted))
        self.assertFalse(is_form_4('"A","B"\n"B"\n"C"'.split("\n"), quoted))
        self.assertFalse(is_form_4('"A@b"\n"B"\n"C"'.split("\n"), quoted))
        self.assertFalse(is_form_4('A\n"-1"\n2'.split("\n"), unquoted))
        self.assertFalse(is_form_4("A B\n-1 3\n2 4".split("\n"), unquoted))

    def test_form_5(self) -> None:
        dialect = SimpleDialect(delimiter=",", quotechar='"', escapechar="")

        self.assertTrue(is_form_5('"A,B"\n"1,2"\n"3,4"'.split("\n"), dialect))
        self.assertTrue(is_form_5('"A,B"\n"1,"\n"2,3"'.split("\n"), dialect))

        self.assertFalse(is_form_5("A,B\n1,2\n3,4".split("\n"), dialect))
        self.assertFalse(is_form_5("A,B\n1,\n2,3".split("\n"), dialect))
        self.assertFalse(
            is_form_5('"A,""B"""\n"1,"\n"2,3"'.split("\n"), dialect)
        )


if __name__ == "__main__":
    unittest.main()
