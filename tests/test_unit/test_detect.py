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

    sample10 = """\
bytearray(b'fake data'),20:53:06,2019-09-01T19:28:21
bytearray(b'fake data'),19:33:15,2005-02-15T19:10:31
bytearray(b'fake data'),10:43:05,1992-10-12T14:49:24
bytearray(b'fake data'),10:36:49,1999-07-18T17:27:55
bytearray(b'fake data'),03:33:35,1982-04-24T17:38:45
bytearray(b'fake data'),14:49:47,1983-01-05T22:17:42
bytearray(b'fake data'),10:35:30,2006-10-27T02:30:45
"""

    sample11 = """\
"{""fake"": ""json"", ""fake2"":""json2""}",13:31:38,06:00:04+01:00
"{""fake"": ""json"", ""fake2"":""json2""}",22:13:29,14:20:11+02:00
"{""fake"": ""json"", ""fake2"":""json2""}",04:37:27,22:04:28+03:00
"{""fake"": ""json"", ""fake2"":""json2""}",04:25:28,23:12:53+01:00
"{""fake"": ""json"", ""fake2"":""json2""}",21:04:15,08:23:58+02:00
"{""fake"": ""json"", ""fake2"":""json2""}",10:37:03,11:06:42+05:30
"{""fake"": ""json"", ""fake2"":""json2""}",10:17:24,23:38:47+06:00
"{""fake"": ""json"", ""fake2"":""json2""}",00:02:51,20:04:45-06:00
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
        dialect = detector.detect(self.sample10)
        self.assertEqual(dialect.delimiter, ",")
        self.assertEqual(dialect.quotechar, "")
        dialect = detector.detect(self.sample11)
        self.assertEqual(dialect.delimiter, ",")
        self.assertEqual(dialect.quotechar, '"')

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
