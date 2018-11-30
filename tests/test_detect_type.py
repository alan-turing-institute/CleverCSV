# -*- coding: utf-8 -*-

"""
Unit tests for the type detection.

Author: Gertjan van den Burg

"""

import unittest

from ccsv.detect_type import TypeDetector, type_score


class TypeDetectorTestCase(unittest.TestCase):
    def setUp(self):
        self.td = TypeDetector()

    """
    NUMBERS
    """

    def test_number(self):
        self.assertTrue(self.td.is_number("1"))
        self.assertTrue(self.td.is_number("2"))
        self.assertTrue(self.td.is_number("34"))
        self.assertTrue(self.td.is_number("56"))
        self.assertTrue(self.td.is_number("123"))
        self.assertTrue(self.td.is_number("789"))
        self.assertTrue(self.td.is_number("132."))
        self.assertTrue(self.td.is_number("0.123"))
        self.assertTrue(self.td.is_number("0.10800212"))
        self.assertTrue(self.td.is_number("0.1231e-087"))
        self.assertTrue(self.td.is_number("10.789e09"))
        self.assertTrue(self.td.is_number("123.256e+08"))
        self.assertTrue(self.td.is_number("0.1231E-087"))
        self.assertTrue(self.td.is_number("10.789E09"))
        self.assertTrue(self.td.is_number("123.256E+08"))
        self.assertTrue(self.td.is_number("123,456,798.00"))
        self.assertTrue(self.td.is_number("23,456.798"))
        self.assertTrue(self.td.is_number("1,234.56"))
        self.assertTrue(self.td.is_number("1,123."))
        self.assertTrue(self.td.is_number("1e5"))
        self.assertTrue(self.td.is_number("1.23e5"))
        self.assertTrue(self.td.is_number("-1"))
        self.assertTrue(self.td.is_number("-2"))
        self.assertTrue(self.td.is_number("-34"))
        self.assertTrue(self.td.is_number("-56"))
        self.assertTrue(self.td.is_number("-123"))
        self.assertTrue(self.td.is_number("-789"))
        self.assertTrue(self.td.is_number("-0.123"))
        self.assertTrue(self.td.is_number("-0.10800212"))
        self.assertTrue(self.td.is_number("-0.1231e-087"))
        self.assertTrue(self.td.is_number("-10.789e09"))
        self.assertTrue(self.td.is_number("-123.256e+08"))
        self.assertTrue(self.td.is_number("-0.1231E-087"))
        self.assertTrue(self.td.is_number("-10.789E09"))
        self.assertTrue(self.td.is_number("-123.256E+08"))
        self.assertTrue(self.td.is_number("-123,456,798.00"))
        self.assertTrue(self.td.is_number("-23,456.798"))
        self.assertTrue(self.td.is_number("-1,234.56"))
        self.assertTrue(self.td.is_number("+1"))
        self.assertTrue(self.td.is_number("+2"))
        self.assertTrue(self.td.is_number("+34"))
        self.assertTrue(self.td.is_number("+56"))
        self.assertTrue(self.td.is_number("+123"))
        self.assertTrue(self.td.is_number("+789"))
        self.assertTrue(self.td.is_number("+0.123"))
        self.assertTrue(self.td.is_number("+0.10800212"))
        self.assertTrue(self.td.is_number("+0.1231e-087"))
        self.assertTrue(self.td.is_number("+10.789e09"))
        self.assertTrue(self.td.is_number("+123.256e+08"))
        self.assertTrue(self.td.is_number("+0.1231E-087"))
        self.assertTrue(self.td.is_number("+10.789E09"))
        self.assertTrue(self.td.is_number("+123.256E+08"))
        self.assertTrue(self.td.is_number("+123,456,798.00"))
        self.assertTrue(self.td.is_number("+23,456.798"))
        self.assertTrue(self.td.is_number("+1,234.56"))
        self.assertTrue(self.td.is_number(".707"))
        self.assertTrue(self.td.is_number("-.707"))
        self.assertTrue(self.td.is_number("50,000.123"))
        self.assertTrue(self.td.is_number("1.000,123"))
        self.assertFalse(self.td.is_number("0000.213654"))
        self.assertFalse(self.td.is_number("123.465.798"))
        self.assertFalse(self.td.is_number("0.5e0.5"))
        self.assertFalse(self.td.is_number("1,23.45"))
        self.assertFalse(self.td.is_number("12,34.56"))
        self.assertFalse(self.td.is_number("+00003"))
        self.assertFalse(self.td.is_number("37.e88"))
        self.assertFalse(self.td.is_number("0,132.6"))
        self.assertFalse(self.td.is_number("1,"))
        self.assertFalse(self.td.is_number(""))
        self.assertFalse(self.td.is_number("E14000537"))

    """
    Type Score tests
    """

    def test_type_score_1(self):
        # theta_1 from paper
        cells = [
            "7",
            "5; Mon",
            " Jan 12;6",
            "40",
            "100; Fri",
            " Mar 21;8",
            "23",
            "8",
            "2; Thu",
            " Sep 17; 2",
            "71",
            "538",
            "0;;7",
            "26",
            '"NA"; Wed',
            " Oct 4;6",
            "93",
        ]
        out = type_score(cells)
        exp = 8 / 17
        self.assertAlmostEqual(exp, out)

    def test_type_score_2(self):
        # theta_2 from paper
        cells = [
            "7,5",
            " Mon, Jan 12",
            "6,40",
            "100",
            " Fri, Mar 21",
            "8,23",
            "8,2",
            " Thu, Sep 17",
            "2,71",
            "538,0",
            "",
            "7,26",
            '"N/A"',
            " Wed, Oct 4",
            "6,93",
        ]
        out = type_score(cells)
        exp = 10 / 15
        self.assertAlmostEqual(exp, out)

    def test_type_score_3(self):
        # theta_3 from paper
        cells = [
            "7,5",
            " Mon, Jan 12",
            "6,40",
            "100",
            " Fri, Mar 21",
            "8,23",
            "8,2",
            " Thu, Sep 17",
            "2,71",
            "538,0",
            "",
            "7,26",
            'N/A',
            " Wed, Oct 4",
            "6,93",
        ]
        out = type_score(cells)
        exp = 11 / 15
        self.assertAlmostEqual(exp, out)



if __name__ == "__main__":
    unittest.main()
