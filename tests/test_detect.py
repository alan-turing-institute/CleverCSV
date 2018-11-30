
# -*- coding: utf-8 -*-

"""
Unit tests for the dialect detection.

Author: Gertjan van den Burg

"""

import unittest

from ccsv.dialect import SimpleDialect
from ccsv.detect import Detector


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
    sample9 = """\
'Harry''s'+ Arlington Heights'+ 'IL'+ '2/1/03'+ 'Kimi Hayes'
'Shark City'+ Glendale Heights'+' IL'+ '12/28/02'+ 'Prezence'
'Tommy''s Place'+ Blue Island'+ 'IL'+ '12/28/02'+ 'Blue Sunday/White Crow'
'Stonecutters ''Seafood'' and Chop House'+ 'Lemont'+ 'IL'+ '12/19/02'+ 'Week Back'
"""

    def test_detect(self):
        detector = Detector()
        dialect = detector.sniff(self.sample1)
        self.assertEqual(dialect.delimiter, ",")
        self.assertEqual(dialect.quotechar, "")
        self.assertEqual(dialect.escapechar, "")

        dialect = detector.sniff(self.sample2)
        self.assertEqual(dialect.delimiter, ":")
        self.assertEqual(dialect.quotechar, "'")
        self.assertEqual(dialect.escapechar, "")
