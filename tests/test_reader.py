# -*- coding: utf-8 -*-

"""
Unit tests for the CSV reader.

Author: Gertjan van den Burg

"""

import unittest

import ccsv


class ReaderTestCase(unittest.TestCase):
    def _read_test(self, input, expect, **kwargs):
        reader = ccsv.reader(input, **kwargs)
        print(reader)
        result = list(reader)
        print(result)
        self.assertEqual(result, expect)

    def test_read_eol(self):
        self._read_test("a,b", [["a", "b"]])
