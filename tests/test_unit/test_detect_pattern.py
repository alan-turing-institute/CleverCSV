# -*- coding: utf-8 -*-

"""
Unit tests for the pattern score.

Author: Gertjan van den Burg

"""

import unittest

from clevercsv import detect_pattern
from clevercsv.dialect import SimpleDialect


class PatternTestCase(unittest.TestCase):

    """
    Abstraction tests
    """

    def test_abstraction_1(self):
        out = detect_pattern.make_abstraction(
            "A,B,C", SimpleDialect(delimiter=",", quotechar="", escapechar="")
        )
        exp = "CDCDC"
        self.assertEqual(exp, out)

    def test_abstraction_2(self):
        out = detect_pattern.make_abstraction(
            "A,\rA,A,A\r",
            SimpleDialect(delimiter=",", quotechar="", escapechar=""),
        )
        exp = "CDCRCDCDC"
        self.assertEqual(exp, out)

    def test_abstraction_3(self):
        out = detect_pattern.make_abstraction(
            "a,a,\n,a,a\ra,a,a\r\n",
            SimpleDialect(delimiter=",", quotechar="", escapechar=""),
        )
        exp = "CDCDCRCDCDCRCDCDC"
        self.assertEqual(exp, out)

    def test_abstraction_4(self):
        out = detect_pattern.make_abstraction(
            'a,"bc""d""e""f""a",\r\n',
            SimpleDialect(delimiter=",", quotechar='"', escapechar=""),
        )
        exp = "CDCDC"
        self.assertEqual(exp, out)

    def test_abstraction_5(self):
        out = detect_pattern.make_abstraction(
            'a,"bc""d"",|"f|""',
            SimpleDialect(delimiter=",", quotechar='"', escapechar="|"),
        )
        exp = "CDC"
        self.assertEqual(exp, out)

    def test_abstraction_6(self):
        out = detect_pattern.make_abstraction(
            ",,,", SimpleDialect(delimiter=",", quotechar="", escapechar="")
        )
        exp = "CDCDCDC"
        self.assertEqual(exp, out)

    def test_abstraction_7(self):
        out = detect_pattern.make_abstraction(
            ',"",,', SimpleDialect(delimiter=",", quotechar='"', escapechar="")
        )
        exp = "CDCDCDC"
        self.assertEqual(exp, out)

    def test_abstraction_8(self):
        out = detect_pattern.make_abstraction(
            ',"",,\r\n',
            SimpleDialect(delimiter=",", quotechar='"', escapechar=""),
        )
        exp = "CDCDCDC"
        self.assertEqual(exp, out)

    """
    Escape char tests
    """

    def test_abstraction_9(self):
        out = detect_pattern.make_abstraction(
            "A,B|,C",
            SimpleDialect(delimiter=",", quotechar="", escapechar="|"),
        )
        exp = "CDC"
        self.assertEqual(exp, out)

    def test_abstraction_10(self):
        out = detect_pattern.make_abstraction(
            'A,"B,C|"D"',
            SimpleDialect(delimiter=",", quotechar='"', escapechar="|"),
        )
        exp = "CDC"
        self.assertEqual(exp, out)

    def test_abstraction_11(self):
        out = detect_pattern.make_abstraction(
            "a,|b,c",
            SimpleDialect(delimiter=",", quotechar="", escapechar="|"),
        )
        exp = "CDCDC"
        self.assertEqual(exp, out)

    def test_abstraction_12(self):
        out = detect_pattern.make_abstraction(
            "a,b|,c",
            SimpleDialect(delimiter=",", quotechar="", escapechar="|"),
        )
        exp = "CDC"
        self.assertEqual(exp, out)

    def test_abstraction_13(self):
        out = detect_pattern.make_abstraction(
            'a,"b,c|""',
            SimpleDialect(delimiter=",", quotechar='"', escapechar="|"),
        )
        exp = "CDC"
        self.assertEqual(exp, out)

    def test_abstraction_14(self):
        out = detect_pattern.make_abstraction(
            "a,b||c",
            SimpleDialect(delimiter=",", quotechar="", escapechar="|"),
        )
        exp = "CDC"
        self.assertEqual(exp, out)

    def test_abstraction_15(self):
        out = detect_pattern.make_abstraction(
            'a,"b|"c||d|"e"',
            SimpleDialect(delimiter=",", quotechar='"', escapechar="|"),
        )
        exp = "CDC"
        self.assertEqual(exp, out)

    def test_abstraction_16(self):
        out = detect_pattern.make_abstraction(
            'a,"b|"c||d","e"',
            SimpleDialect(delimiter=",", quotechar='"', escapechar="|"),
        )
        exp = "CDCDC"
        self.assertEqual(exp, out)

    """
    Fill empties
    """

    def test_fill_empties_1(self):
        out = detect_pattern.fill_empties("DDD")
        exp = "CDCDCDC"
        self.assertEqual(exp, out)

    """
    Pattern Score tests
    """

    def test_pattern_score_1(self):
        # theta_1 from paper
        data = (
            "7,5; Mon, Jan 12;6,40\n100; Fri, Mar 21;8,23\n8,2; Thu, Sep 17;"
            '2,71\n538,0;;7,26\n"NA"; Wed, Oct 4;6,93'
        )
        d = SimpleDialect(delimiter=",", quotechar="", escapechar="")
        out = detect_pattern.pattern_score(data, d)
        exp = 7 / 4
        self.assertAlmostEqual(exp, out)

    def test_pattern_score_2(self):
        # theta_2 from paper
        data = (
            "7,5; Mon, Jan 12;6,40\n100; Fri, Mar 21;8,23\n8,2; Thu, Sep 17;"
            '2,71\n538,0;;7,26\n"NA"; Wed, Oct 4;6,93'
        )
        d = SimpleDialect(delimiter=";", quotechar="", escapechar="")
        out = detect_pattern.pattern_score(data, d)
        exp = 10 / 3
        self.assertAlmostEqual(exp, out)

    def test_pattern_score_3(self):
        # theta_3 from paper
        data = (
            "7,5; Mon, Jan 12;6,40\n100; Fri, Mar 21;8,23\n8,2; Thu, Sep 17;"
            '2,71\n538,0;;7,26\n"NA"; Wed, Oct 4;6,93'
        )
        d = SimpleDialect(delimiter=";", quotechar='"', escapechar="")
        out = detect_pattern.pattern_score(data, d)
        exp = 10 / 3
        self.assertAlmostEqual(exp, out)


if __name__ == "__main__":
    unittest.main()
