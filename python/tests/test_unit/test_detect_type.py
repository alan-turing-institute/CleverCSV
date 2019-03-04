# -*- coding: utf-8 -*-

"""
Unit tests for the type detection.

Author: Gertjan van den Burg

"""

import unittest

from ccsv.dialect import SimpleDialect
from ccsv.detect_type import TypeDetector, type_score


class TypeDetectorTestCase(unittest.TestCase):
    def setUp(self):
        self.td = TypeDetector()

    """
    NUMBERS
    """

    def test_number(self):
        yes_number = [
            "1",
            "2",
            "34",
            "56",
            "123",
            "789",
            "132.",
            "0.123",
            "0.10800212",
            "0.1231e-087",
            "10.789e09",
            "123.256e+08",
            "0.1231E-087",
            "10.789E09",
            "123.256E+08",
            "123,456,798.00",
            "23,456.798",
            "1,234.56",
            "1,123.",
            "1e5",
            "1.23e5",
            "-1",
            "-2",
            "-34",
            "-56",
            "-123",
            "-789",
            "-0.123",
            "-0.10800212",
            "-0.1231e-087",
            "-10.789e09",
            "-123.256e+08",
            "-0.1231E-087",
            "-10.789E09",
            "-123.256E+08",
            "-123,456,798.00",
            "-23,456.798",
            "-1,234.56",
            "+1",
            "+2",
            "+34",
            "+56",
            "+123",
            "+789",
            "+0.123",
            "+0.10800212",
            "+0.1231e-087",
            "+10.789e09",
            "+123.256e+08",
            "+0.1231E-087",
            "+10.789E09",
            "+123.256E+08",
            "+123,456,798.00",
            "+23,456.798",
            "+1,234.56",
            ".707",
            "-.707",
            "50,000.123",
            "1.000,123",
            "37.e88",
            "1.",
        ]
        for num in yes_number:
            with self.subTest(num=num):
                self.assertTrue(self.td.is_number(num))
        no_number = [
            "0000.213654",
            "123.465.798",
            "0.5e0.5",
            "1,23.45",
            "12,34.56",
            "+00003",
            "0,132.6",
            "1,",
            "",
            "E14000537",
            "0e",
            ".",
            ",",
            "+E3",
            "1,",
        ]
        for num in no_number:
            with self.subTest(num=num):
                self.assertFalse(self.td.is_number(num))

    """
    Type Score tests
    """

    def test_type_score_1(self):
        # theta_1 from paper
        cells = [
            ["7", "5; Mon", " Jan 12;6", "40"],
            ["100; Fri", " Mar 21;8", "23"],
            ["8", "2; Thu", " Sep 17; 2", "71"],
            ["538", "0;;7", "26"],
            ['"NA"; Wed', " Oct 4;6", "93"],
        ]
        data = "\n".join([",".join(x) for x in cells])
        dialect = SimpleDialect(delimiter=",", quotechar="", escapechar="")
        out = type_score(data, dialect)
        exp = 8 / 17
        self.assertAlmostEqual(exp, out)

    def test_type_score_2(self):
        # theta_2 from paper
        cells = [
            ["7,5", " Mon, Jan 12", "6,40"],
            ["100", " Fri, Mar 21", "8,23"],
            ["8,2", " Thu, Sep 17", "2,71"],
            ["538,0", "", "7,26"],
            ['"N/A"', " Wed, Oct 4", "6,93"],
        ]
        data = "\r\n".join([";".join(x) for x in cells])
        dialect = SimpleDialect(delimiter=";", quotechar="", escapechar="")
        out = type_score(data, dialect)
        exp = 10 / 15
        self.assertAlmostEqual(exp, out)

    def test_type_score_3(self):
        # theta_3 from paper
        cells = [
            ["7,5", " Mon, Jan 12", "6,40"],
            ["100", " Fri, Mar 21", "8,23"],
            ["8,2", " Thu, Sep 17", "2,71"],
            ["538,0", "", "7,26"],
            ["N/A", " Wed, Oct 4", "6,93"],
        ]
        data = "\r".join([";".join(x) for x in cells])
        dialect = SimpleDialect(delimiter=";", quotechar='"', escapechar="")
        out = type_score(data, dialect)
        exp = 11 / 15
        self.assertAlmostEqual(exp, out)


if __name__ == "__main__":
    unittest.main()
