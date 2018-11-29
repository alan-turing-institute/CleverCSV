# -*- coding: utf-8 -*-

"""
Unit tests for the type detection.

Author: Gertjan van den Burg

"""

import unittest

from ccsv.type_detect import TypeDetector, type_score


class TypeDetectorTestCase(unittest.TestCase):
    def setUp(self):
        self.td = TypeDetector()

    """
    NUMBERS
    """

    def test_number_true_1(self):
        self.assertTrue(self.td.is_number("1"))

    def test_number_true_2(self):
        self.assertTrue(self.td.is_number("2"))

    def test_number_true_3(self):
        self.assertTrue(self.td.is_number("34"))

    def test_number_true_4(self):
        self.assertTrue(self.td.is_number("56"))

    def test_number_true_5(self):
        self.assertTrue(self.td.is_number("123"))

    def test_number_true_6(self):
        self.assertTrue(self.td.is_number("789"))

    def test_number_true_7(self):
        self.assertTrue(self.td.is_number("132."))

    def test_number_true_8(self):
        self.assertTrue(self.td.is_number("0.123"))

    def test_number_true_9(self):
        self.assertTrue(self.td.is_number("0.10800212"))

    def test_number_true_10(self):
        self.assertTrue(self.td.is_number("0.1231e-087"))

    def test_number_true_11(self):
        self.assertTrue(self.td.is_number("10.789e09"))

    def test_number_true_12(self):
        self.assertTrue(self.td.is_number("123.256e+08"))

    def test_number_true_13(self):
        self.assertTrue(self.td.is_number("0.1231E-087"))

    def test_number_true_14(self):
        self.assertTrue(self.td.is_number("10.789E09"))

    def test_number_true_15(self):
        self.assertTrue(self.td.is_number("123.256E+08"))

    def test_number_true_16(self):
        self.assertTrue(self.td.is_number("123,456,798.00"))

    def test_number_true_17(self):
        self.assertTrue(self.td.is_number("23,456.798"))

    def test_number_true_18(self):
        self.assertTrue(self.td.is_number("1,234.56"))

    def test_number_true_19(self):
        self.assertTrue(self.td.is_number("1,123."))

    def test_number_true_20(self):
        self.assertTrue(self.td.is_number("1e5"))

    def test_number_true_21(self):
        self.assertTrue(self.td.is_number("1.23e5"))

    def test_number_true_22(self):
        self.assertTrue(self.td.is_number("-1"))

    def test_number_true_23(self):
        self.assertTrue(self.td.is_number("-2"))

    def test_number_true_24(self):
        self.assertTrue(self.td.is_number("-34"))

    def test_number_true_25(self):
        self.assertTrue(self.td.is_number("-56"))

    def test_number_true_26(self):
        self.assertTrue(self.td.is_number("-123"))

    def test_number_true_27(self):
        self.assertTrue(self.td.is_number("-789"))

    def test_number_true_28(self):
        self.assertTrue(self.td.is_number("-0.123"))

    def test_number_true_29(self):
        self.assertTrue(self.td.is_number("-0.10800212"))

    def test_number_true_30(self):
        self.assertTrue(self.td.is_number("-0.1231e-087"))

    def test_number_true_31(self):
        self.assertTrue(self.td.is_number("-10.789e09"))

    def test_number_true_32(self):
        self.assertTrue(self.td.is_number("-123.256e+08"))

    def test_number_true_33(self):
        self.assertTrue(self.td.is_number("-0.1231E-087"))

    def test_number_true_34(self):
        self.assertTrue(self.td.is_number("-10.789E09"))

    def test_number_true_35(self):
        self.assertTrue(self.td.is_number("-123.256E+08"))

    def test_number_true_36(self):
        self.assertTrue(self.td.is_number("-123,456,798.00"))

    def test_number_true_37(self):
        self.assertTrue(self.td.is_number("-23,456.798"))

    def test_number_true_38(self):
        self.assertTrue(self.td.is_number("-1,234.56"))

    def test_number_true_39(self):
        self.assertTrue(self.td.is_number("+1"))

    def test_number_true_40(self):
        self.assertTrue(self.td.is_number("+2"))

    def test_number_true_41(self):
        self.assertTrue(self.td.is_number("+34"))

    def test_number_true_42(self):
        self.assertTrue(self.td.is_number("+56"))

    def test_number_true_43(self):
        self.assertTrue(self.td.is_number("+123"))

    def test_number_true_44(self):
        self.assertTrue(self.td.is_number("+789"))

    def test_number_true_45(self):
        self.assertTrue(self.td.is_number("+0.123"))

    def test_number_true_46(self):
        self.assertTrue(self.td.is_number("+0.10800212"))

    def test_number_true_47(self):
        self.assertTrue(self.td.is_number("+0.1231e-087"))

    def test_number_true_48(self):
        self.assertTrue(self.td.is_number("+10.789e09"))

    def test_number_true_49(self):
        self.assertTrue(self.td.is_number("+123.256e+08"))

    def test_number_true_50(self):
        self.assertTrue(self.td.is_number("+0.1231E-087"))

    def test_number_true_51(self):
        self.assertTrue(self.td.is_number("+10.789E09"))

    def test_number_true_52(self):
        self.assertTrue(self.td.is_number("+123.256E+08"))

    def test_number_true_53(self):
        self.assertTrue(self.td.is_number("+123,456,798.00"))

    def test_number_true_54(self):
        self.assertTrue(self.td.is_number("+23,456.798"))

    def test_number_true_55(self):
        self.assertTrue(self.td.is_number("+1,234.56"))

    def test_number_true_56(self):
        self.assertTrue(self.td.is_number(".707"))

    def test_number_true_57(self):
        self.assertTrue(self.td.is_number("-.707"))

    def test_number_true_58(self):
        self.assertTrue(self.td.is_number("50,000.123"))

    def test_number_true_59(self):
        self.assertTrue(self.td.is_number("1.000,123"))

    def test_number_false_1(self):
        self.assertFalse(self.td.is_number("0000.213654"))

    def test_number_false_2(self):
        self.assertFalse(self.td.is_number("123.465.798"))

    def test_number_false_3(self):
        self.assertFalse(self.td.is_number("0.5e0.5"))

    def test_number_false_4(self):
        self.assertFalse(self.td.is_number("1,23.45"))

    def test_number_false_5(self):
        self.assertFalse(self.td.is_number("12,34.56"))

    def test_number_false_6(self):
        self.assertFalse(self.td.is_number("+00003"))

    def test_number_false_7(self):
        self.assertFalse(self.td.is_number("37.e88"))

    def test_number_false_8(self):
        self.assertFalse(self.td.is_number("0,132.6"))

    def test_number_false_9(self):
        self.assertFalse(self.td.is_number("1,"))

    def test_number_false_10(self):
        self.assertFalse(self.td.is_number(""))

    def test_number_false_11(self):
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
