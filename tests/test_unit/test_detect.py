# -*- coding: utf-8 -*-

"""
Unit tests for the dialect detection.

Author: Gertjan van den Burg

"""

import unittest

from clevercsv.detect import Detector


class DetectorTestCase(unittest.TestCase):
    # Initially we copy the results from CPython test suite.

    sample1 = """\
Harry's, Arlington Heights, IL, 2/1/03, Kimi Hayes
Shark City, Glendale Heights, IL, 12/28/02, Prezence
Tommy's Place, Blue Island, IL, 12/28/02, Blue Sunday/White Crow
Stonecutters Seafood and Chop House, Lemont, IL, 12/19/02, Week Back
"""
    sample2 = """\
'Harry''s':'Arlington Heights':'IL':'2/1/03':'Kimi Hayes'
'Shark City':'Glendale Heights':'IL':'12/28/02':'Prezence'
'Tommy''s Place':'Blue Island':'IL':'12/28/02':'Blue Sunday/White Crow'
'Stonecutters ''Seafood'' and Chop House':'Lemont':'IL':'12/19/02':'Week Back'
"""
    header1 = """\
"venue","city","state","date","performers"
"""
    sample3 = """\
05/05/03?05/05/03?05/05/03?05/05/03?05/05/03?05/05/03
05/05/03?05/05/03?05/05/03?05/05/03?05/05/03?05/05/03
05/05/03?05/05/03?05/05/03?05/05/03?05/05/03?05/05/03
"""

    sample4 = """\
2147483648;43.0e12;17;abc;def
147483648;43.0e2;17;abc;def
47483648;43.0;170;abc;def
"""

    sample5 = "aaa\tbbb\r\nAAA\t\r\nBBB\t\r\n"
    sample6 = "a|b|c\r\nd|e|f\r\n"
    sample7 = "'a'|'b'|'c'\r\n'd'|e|f\r\n"

    header2 = """\
"venue"+"city"+"state"+"date"+"performers"
"""
    sample8 = """\
Harry's+ Arlington Heights+ IL+ 2/1/03+ Kimi Hayes
Shark City+ Glendale Heights+ IL+ 12/28/02+ Prezence
Tommy's Place+ Blue Island+ IL+ 12/28/02+ Blue Sunday/White Crow
Stonecutters Seafood and Chop House+ Lemont+ IL+ 12/19/02+ Week Back
"""
    # adapted to be not broken
    sample9 = """\
'Harry''s'+ 'Arlington Heights'+ 'IL'+ '2/1/03'+ 'Kimi Hayes'
'Shark City'+ 'Glendale Heights'+' IL'+ '12/28/02'+ 'Prezence'
'Tommy''s Place'+ 'Blue Island'+ 'IL'+ '12/28/02'+ 'Blue Sunday/White Crow'
'Stonecutters ''Seafood'' and Chop House'+ 'Lemont'+ 'IL'+ '12/19/02'+ 'Week Back'
"""

    def test_detect(self):
        # Adapted from CPython
        detector = Detector()
        dialect = detector.detect(self.sample1)
        self.assertEqual(dialect.delimiter, ",")
        self.assertEqual(dialect.quotechar, "")
        self.assertEqual(dialect.escapechar, "")

        dialect = detector.detect(self.sample2)
        self.assertEqual(dialect.delimiter, ":")
        self.assertEqual(dialect.quotechar, "'")
        self.assertEqual(dialect.escapechar, "")

    def test_delimiters(self):
        # Adapted from CPython
        detector = Detector()
        dialect = detector.detect(self.sample3)
        self.assertIn(dialect.delimiter, self.sample3)
        dialect = detector.detect(self.sample3, delimiters="?,")
        self.assertEqual(dialect.delimiter, "?")
        dialect = detector.detect(self.sample3, delimiters="/,")
        self.assertEqual(dialect.delimiter, "/")
        dialect = detector.detect(self.sample4)
        self.assertEqual(dialect.delimiter, ";")
        dialect = detector.detect(self.sample5)
        self.assertEqual(dialect.delimiter, "\t")
        dialect = detector.detect(self.sample6)
        self.assertEqual(dialect.delimiter, "|")
        dialect = detector.detect(self.sample7)
        self.assertEqual(dialect.delimiter, "|")
        self.assertEqual(dialect.quotechar, "'")
        dialect = detector.detect(self.sample8)
        self.assertEqual(dialect.delimiter, "+")
        dialect = detector.detect(self.sample9)
        self.assertEqual(dialect.delimiter, "+")
        self.assertEqual(dialect.quotechar, "'")

    def test_has_header(self):
        detector = Detector()
        self.assertEqual(detector.has_header(self.sample1), False)
        self.assertEqual(
            detector.has_header(self.header1 + self.sample1), True
        )

    def test_has_header_regex_special_delimiter(self):
        detector = Detector()
        self.assertEqual(detector.has_header(self.sample8), False)
        self.assertEqual(
            detector.has_header(self.header2 + self.sample8), True
        )


if __name__ == "__main__":
    unittest.main()
