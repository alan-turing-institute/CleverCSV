# -*- coding: utf-8 -*-

"""
Our CSV parser.

Author: Gertjan van den Burg

"""

import unittest

from ccsv.parser import parse_file


class ParserTestCase(unittest.TestCase):

    """
    Testing splitting on delimiter with or without quotes
    """

    def test_parse_simple_1(self):
        out = parse_file("A,B,C,D,E", delimiter=",", quotechar='"')
        exp = [["A", "B", "C", "D", "E"]]
        self.assertEqual(exp, out)

    def test_parse_simple_2(self):
        out = parse_file("A,B,C,D,E", delimiter=",", quotechar="")
        exp = [["A", "B", "C", "D", "E"]]
        self.assertEqual(exp, out)

    def test_parse_simple_3(self):
        out = parse_file("A,B,C,D,E")
        exp = [["A,B,C,D,E"]]
        self.assertEqual(exp, out)

    def test_parse_simple_4(self):
        out = parse_file('A,"B",C,D,E', delimiter=",", quotechar='"')
        exp = [["A", "B", "C", "D", "E"]]
        self.assertEqual(exp, out)

    def test_parse_simple_5(self):
        out = parse_file('A,"B,C",D,E', delimiter=",", quotechar='"')
        exp = [["A", "B,C", "D", "E"]]
        self.assertEqual(exp, out)

    def test_parse_simple_6(self):
        out = parse_file('A,"B,C",D,E', delimiter=",", quotechar="")
        exp = [["A", '"B', 'C"', "D", "E"]]
        self.assertEqual(exp, out)

    def test_parse_simple_7(self):
        out = parse_file('"A","B","C",,,,', delimiter=",", quotechar="")
        exp = [['"A"', '"B"', '"C"', "", "", "", ""]]
        self.assertEqual(exp, out)

    """
    Testing splitting on rows only:
    """

    def test_parse_no_delim_1(self):
        out = parse_file('A"B"C\rA"B""C""D"', quotechar="")
        exp = [['A"B"C'], ['A"B""C""D"']]
        self.assertEqual(exp, out)

    def test_parse_no_delim_2(self):
        out = parse_file('A"B"C\nA"B""C""D"', quotechar="")
        exp = [['A"B"C'], ['A"B""C""D"']]
        self.assertEqual(exp, out)

    def test_parse_no_delim_3(self):
        out = parse_file('A"B"C\r\nA"B""C""D"', quotechar="")
        exp = [['A"B"C'], ['A"B""C""D"']]
        self.assertEqual(exp, out)

    def test_parse_no_delim_4(self):
        out = parse_file('A"B\r\nB"C\r\nD"E"F\r\nG', quotechar='"')
        exp = [['A"B\r\nB"C'], ['D"E"F'], ["G"]]
        self.assertEqual(exp, out)

    def test_parse_no_delim_5(self):
        out = parse_file('A"B\nB"C\nD"E"F\nG', quotechar='"')
        exp = [['A"B\nB"C'], ['D"E"F'], ["G"]]
        self.assertEqual(exp, out)

    def test_parse_no_delim_6(self):
        out = parse_file('A"B\nB\rB"C\nD"E"F\nG', quotechar='"')
        exp = [['A"B\nB\rB"C'], ['D"E"F'], ["G"]]
        self.assertEqual(exp, out)

    """
    Tests from Pythons builtin CSV module:
    """

    def test_parse_builtin_1(self):
        out = parse_file("")
        exp = []
        self.assertEqual(exp, out)

    def test_parse_builtin_2(self):
        out = parse_file("a,b\r", delimiter=",")
        exp = [["a", "b"]]
        self.assertEqual(exp, out)

    def test_parse_builtin_3(self):
        out = parse_file("a,b\n", delimiter=",")
        exp = [["a", "b"]]
        self.assertEqual(exp, out)

    def test_parse_builtin_4(self):
        out = parse_file("a,b\r\n", delimiter=",")
        exp = [["a", "b"]]
        self.assertEqual(exp, out)

    def test_parse_builtin_5(self):
        out = parse_file('a,"', delimiter=",", quotechar='"')
        exp = [["a", ""]]
        self.assertEqual(exp, out)

    def test_parse_builtin_6(self):
        out = parse_file('"a', delimiter=",", quotechar='"')
        exp = [["a"]]
        self.assertEqual(exp, out)

    def test_parse_builtin_7(self):
        # differs from Python (1)
        out = parse_file("a,|b,c", delimiter=",", quotechar='"', escapechar="|")
        exp = [["a", "|b", "c"]]
        self.assertEqual(exp, out)

    def test_parse_builtin_8(self):
        out = parse_file("a,b|,c", delimiter=",", quotechar='"', escapechar="|")
        exp = [["a", "b,c"]]
        self.assertEqual(exp, out)

    def test_parse_builtin_9(self):
        # differs from Python (1)
        out = parse_file(
            'a,"b,|c"', delimiter=",", quotechar='"', escapechar="|"
        )
        exp = [["a", "b,|c"]]
        self.assertEqual(exp, out)

    def test_parse_builtin_10(self):
        out = parse_file(
            'a,"b,c|""', delimiter=",", quotechar='"', escapechar="|"
        )
        exp = [["a", 'b,c"']]
        self.assertEqual(exp, out)

    def test_parse_builtin_11(self):
        # differs from Python (2)
        out = parse_file(
            'a,"b,c"|', delimiter=",", quotechar='"', escapechar="|"
        )
        exp = [["a", "b,c"]]
        self.assertEqual(exp, out)

    def test_parse_builtin_12(self):
        out = parse_file('1,",3,",5', delimiter=",", quotechar='"')
        exp = [["1", ",3,", "5"]]
        self.assertEqual(exp, out)

    def test_parse_builtin_13(self):
        out = parse_file('1,",3,",5', delimiter=",", quotechar="")
        exp = [["1", '"', "3", '"', "5"]]
        self.assertEqual(exp, out)

    def test_parse_builtin_14(self):
        out = parse_file(',3,"5",7.3, 9', delimiter=",", quotechar='"')
        exp = [["", "3", "5", "7.3", " 9"]]
        self.assertEqual(exp, out)

    def test_parse_builtin_15(self):
        out = parse_file('"a\nb", 7', delimiter=",", quotechar='"')
        exp = [["a\nb", " 7"]]
        self.assertEqual(exp, out)

    """
    Double quotes:
    """

    def test_parse_dq_1(self):
        out = parse_file('a,"a""b""c"', delimiter=",", quotechar='"')
        exp = [["a", 'a"b"c']]
        self.assertEqual(exp, out)

    """
    Mix double and escapechar:
    """

    def test_parse_mix_double_escape_1(self):
        out = parse_file(
            'a,"bc""d"",|"f|""', delimiter=",", quotechar='"', escapechar="|"
        )
        exp = [["a", 'bc"d","f"']]
        self.assertEqual(exp, out)

    """
    Other tests:
    """

    def test_parse_other_1(self):
        out = parse_file('a,b "c" d,e', delimiter=",", quotechar="")
        exp = [["a", 'b "c" d', "e"]]
        self.assertEqual(exp, out)

    def test_parse_other_2(self):
        out = parse_file('a,b "c" d,e', delimiter=",", quotechar='"')
        exp = [["a", 'b "c" d', "e"]]
        self.assertEqual(exp, out)

    def test_parse_other_3(self):
        out = parse_file("a,\rb,c", delimiter=",")
        exp = [["a", ""], ["b", "c"]]
        self.assertEqual(exp, out)

    def test_parse_other_4(self):
        out = parse_file("a,b\r\n\r\nc,d\r\n", delimiter=",")
        exp = [["a", "b"], ["c", "d"]]
        self.assertEqual(exp, out)

    def test_parse_other_5(self):
        out = parse_file("\r\na,b\rc,d\n\re,f\r\n", delimiter=",")
        exp = [["a", "b"], ["c", "d"], ["e", "f"]]
        self.assertEqual(exp, out)

    """
    Further escape char tests:
    """

    def test_parse_escape_1(self):
        out = parse_file(
            "a,b,c||d", delimiter=",", quotechar="", escapechar="|"
        )
        exp = [["a", "b", "c|d"]]
        self.assertEqual(exp, out)

    def test_parse_escape_2(self):
        out = parse_file(
            "a,b,c||d,e|,d", delimiter=",", quotechar="", escapechar="|"
        )
        exp = [["a", "b", "c|d", "e,d"]]
        self.assertEqual(exp, out)

    """
    Quote mismatch until EOF:
    """

    def test_parse_quote_mismatch_1(self):
        out = parse_file('a,b,c"d,e\n', delimiter=",", quotechar='"')
        exp = [["a", "b", 'c"d,e\n']]
        self.assertEqual(exp, out)

    def test_parse_quote_mismatch_2(self):
        out = parse_file('a,b,c"d,e\n', delimiter=",", quotechar="")
        exp = [["a", "b", 'c"d', "e"]]
        self.assertEqual(exp, out)

    def test_parse_quote_mismatch_3(self):
        out = parse_file('a,b,"c,d', delimiter=",", quotechar='"')
        exp = [["a", "b", "c,d"]]
        self.assertEqual(exp, out)

    def test_parse_quote_mismatch_4(self):
        out = parse_file('a,b,"c,d\n', delimiter=",", quotechar='"')
        exp = [["a", "b", "c,d\n"]]
        self.assertEqual(exp, out)

    """
    Single column:
    """

    def test_parse_single_1(self):
        out = parse_file("a\rb\rc\n")
        exp = [["a"], ["b"], ["c"]]
        self.assertEqual(exp, out)

    """
    These tests illustrate a difference with the Python parser, which in this
    case would return ``[['a', 'abc', 'd']]``.
    """

    def test_parse_differ_1(self):
        out = parse_file('a,"ab"c,d', delimiter=",", quotechar="")
        exp = [["a", '"ab"c', "d"]]
        self.assertEqual(exp, out)

    def test_parse_differ_2(self):
        out = parse_file('a,"ab"c,d', delimiter=",", quotechar='"')
        exp = [["a", '"ab"c', "d"]]
        self.assertEqual(exp, out)


if __name__ == "__main__":
    unittest.main()
