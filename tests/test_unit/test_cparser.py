# -*- coding: utf-8 -*-

"""
Unit tests for the CSV parser.

Author: Gertjan van den Burg

"""

import io
import unittest

from clevercsv.cparser_util import parse_data


class ParserTestCase(unittest.TestCase):

    """
    Testing splitting on delimiter with or without quotes
    """

    def _parse_test(self, string, expect, **kwargs):
        buf = io.StringIO(string, newline="")
        result = list(parse_data(buf, **kwargs))
        self.assertEqual(result, expect)

    def test_parse_simple_1(self):
        self._parse_test(
            "A,B,C,D,E",
            [["A", "B", "C", "D", "E"]],
            delimiter=",",
            quotechar='"',
        )

    def test_parse_simple_2(self):
        self._parse_test(
            "A,B,C,D,E",
            [["A", "B", "C", "D", "E"]],
            delimiter=",",
            quotechar="",
        )

    def test_parse_simple_3(self):
        self._parse_test("A,B,C,D,E", [["A,B,C,D,E"]])

    def test_parse_simple_4(self):
        self._parse_test(
            'A,"B",C,D,E',
            [["A", "B", "C", "D", "E"]],
            delimiter=",",
            quotechar='"',
        )

    def test_parse_simple_5(self):
        self._parse_test(
            'A,"B,C",D,E',
            [["A", "B,C", "D", "E"]],
            delimiter=",",
            quotechar='"',
        )

    def test_parse_simple_6(self):
        self._parse_test(
            'A,"B,C",D,E',
            [["A", '"B', 'C"', "D", "E"]],
            delimiter=",",
            quotechar="",
        )

    def test_parse_simple_7(self):
        self._parse_test(
            '"A","B","C",,,,',
            [['"A"', '"B"', '"C"', "", "", "", ""]],
            delimiter=",",
            quotechar="",
        )

    """
    Testing splitting on rows only:
    """

    def test_parse_no_delim_1(self):
        self._parse_test(
            'A"B"C\rA"B""C""D"', [['A"B"C'], ['A"B""C""D"']], quotechar=""
        )

    def test_parse_no_delim_2(self):
        self._parse_test(
            'A"B"C\nA"B""C""D"', [['A"B"C'], ['A"B""C""D"']], quotechar=""
        )

    def test_parse_no_delim_3(self):
        self._parse_test(
            'A"B"C\r\nA"B""C""D"', [['A"B"C'], ['A"B""C""D"']], quotechar=""
        )

    def test_parse_no_delim_4(self):
        self._parse_test(
            'A"B\r\nB"C\r\nD"E"F\r\nG',
            [['A"B\r\nB"C'], ['D"E"F'], ["G"]],
            quotechar='"',
        )

    def test_parse_no_delim_5(self):
        self._parse_test(
            'A"B\nB"C\nD"E"F\nG',
            [['A"B\nB"C'], ['D"E"F'], ["G"]],
            quotechar='"',
        )

    def test_parse_no_delim_6(self):
        self._parse_test(
            'A"B\nB\rB"C\nD"E"F\nG',
            [['A"B\nB\rB"C'], ['D"E"F'], ["G"]],
            quotechar='"',
        )

    """
    Tests from Pythons builtin CSV module:
    """

    def test_parse_builtin_1(self):
        self._parse_test("", [])

    def test_parse_builtin_2(self):
        self._parse_test("a,b\r", [["a", "b"]], delimiter=",")

    def test_parse_builtin_3(self):
        self._parse_test("a,b\n", [["a", "b"]], delimiter=",")

    def test_parse_builtin_4(self):
        self._parse_test("a,b\r\n", [["a", "b"]], delimiter=",")

    def test_parse_builtin_5(self):
        self._parse_test('a,"', [["a", ""]], delimiter=",", quotechar='"')

    def test_parse_builtin_6(self):
        self._parse_test('"a', [["a"]], delimiter=",", quotechar='"')

    def test_parse_builtin_7(self):
        # differs from Python (1)
        self._parse_test(
            "a,|b,c",
            [["a", "|b", "c"]],
            delimiter=",",
            quotechar='"',
            escapechar="|",
        )

    def test_parse_builtin_8(self):
        self._parse_test(
            "a,b|,c",
            [["a", "b,c"]],
            delimiter=",",
            quotechar='"',
            escapechar="|",
        )

    def test_parse_builtin_9(self):
        # differs from Python (1)
        self._parse_test(
            'a,"b,|c"',
            [["a", "b,|c"]],
            delimiter=",",
            quotechar='"',
            escapechar="|",
        )

    def test_parse_builtin_10(self):
        self._parse_test(
            'a,"b,c|""',
            [["a", 'b,c"']],
            delimiter=",",
            quotechar='"',
            escapechar="|",
        )

    def test_parse_builtin_11(self):
        # differs from Python (2)
        self._parse_test(
            'a,"b,c"|',
            [["a", "b,c"]],
            delimiter=",",
            quotechar='"',
            escapechar="|",
        )

    def test_parse_builtin_12(self):
        self._parse_test(
            '1,",3,",5', [["1", ",3,", "5"]], delimiter=",", quotechar='"'
        )

    def test_parse_builtin_13(self):
        self._parse_test(
            '1,",3,",5',
            [["1", '"', "3", '"', "5"]],
            delimiter=",",
            quotechar="",
        )

    def test_parse_builtin_14(self):
        self._parse_test(
            ',3,"5",7.3, 9',
            [["", "3", "5", "7.3", " 9"]],
            delimiter=",",
            quotechar='"',
        )

    def test_parse_builtin_15(self):
        self._parse_test(
            '"a\nb", 7', [["a\nb", " 7"]], delimiter=",", quotechar='"'
        )

    """
    Double quotes:
    """

    def test_parse_dq_1(self):
        self._parse_test(
            'a,"a""b""c"', [["a", 'a"b"c']], delimiter=",", quotechar='"'
        )

    def test_parse_dq_2(self):
        self._parse_test(
            'a,"a""b,c""d",e',
            [["a", 'a"b,c"d', "e"]],
            delimiter=",",
            quotechar='"',
        )

    """
    Mix double and escapechar:
    """

    def test_parse_mix_double_escape_1(self):
        self._parse_test(
            'a,"bc""d"",|"f|""',
            [["a", 'bc"d","f"']],
            delimiter=",",
            quotechar='"',
            escapechar="|",
        )

    """
    Other tests:
    """

    def test_parse_other_1(self):
        self._parse_test(
            'a,b "c" d,e', [["a", 'b "c" d', "e"]], delimiter=",", quotechar=""
        )

    def test_parse_other_2(self):
        self._parse_test(
            'a,b "c" d,e',
            [["a", 'b "c" d', "e"]],
            delimiter=",",
            quotechar='"',
        )

    def test_parse_other_3(self):
        self._parse_test("a,\rb,c", [["a", ""], ["b", "c"]], delimiter=",")

    def test_parse_other_4(self):
        self._parse_test(
            "a,b\r\n\r\nc,d\r\n", [["a", "b"], [], ["c", "d"]], delimiter=","
        )

    def test_parse_other_5(self):
        self._parse_test(
            "\r\na,b\rc,d\n\re,f\r\n",
            [[], ["a", "b"], ["c", "d"], [], ["e", "f"]],
            delimiter=",",
        )

    def test_parse_other_6(self):
        self._parse_test(
            "a,b\n\nc,d", [["a", "b"], [], ["c", "d"]], delimiter=","
        )

    """
    Further escape char tests:
    """

    def test_parse_escape_1(self):
        self._parse_test(
            "a,b,c||d",
            [["a", "b", "c|d"]],
            delimiter=",",
            quotechar="",
            escapechar="|",
        )

    def test_parse_escape_2(self):
        self._parse_test(
            "a,b,c||d,e|,d",
            [["a", "b", "c|d", "e,d"]],
            delimiter=",",
            quotechar="",
            escapechar="|",
        )

    """
    Quote mismatch until EOF:
    """

    def test_parse_quote_mismatch_1(self):
        self._parse_test(
            'a,b,c"d,e\n',
            [["a", "b", 'c"d,e\n']],
            delimiter=",",
            quotechar='"',
        )

    def test_parse_quote_mismatch_2(self):
        self._parse_test(
            'a,b,c"d,e\n',
            [["a", "b", 'c"d', "e"]],
            delimiter=",",
            quotechar="",
        )

    def test_parse_quote_mismatch_3(self):
        self._parse_test(
            'a,b,"c,d', [["a", "b", "c,d"]], delimiter=",", quotechar='"'
        )

    def test_parse_quote_mismatch_4(self):
        self._parse_test(
            'a,b,"c,d\n', [["a", "b", "c,d\n"]], delimiter=",", quotechar='"'
        )

    """
    Single column:
    """

    def test_parse_single_1(self):
        self._parse_test("a\rb\rc\n", [["a"], ["b"], ["c"]])

    """
    These tests illustrate a difference with the Python parser, which in this
    case would return ``[['a', 'abc', 'd']]``.
    """

    def test_parse_differ_1(self):
        self._parse_test(
            'a,"ab"c,d', [["a", '"ab"c', "d"]], delimiter=",", quotechar=""
        )

    def test_parse_differ_2(self):
        self._parse_test(
            'a,"ab"c,d', [["a", '"ab"c', "d"]], delimiter=",", quotechar='"'
        )


if __name__ == "__main__":
    unittest.main()
