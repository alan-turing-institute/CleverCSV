# -*- coding: utf-8 -*-

"""
Unit tests based on fuzzing

"""

import unittest

import clevercsv


class FuzzingTestCase(unittest.TestCase):
    def test_sniffer_fuzzing(self):
        strings = ['"""', "```", "\"'", "'@'", "'\"", "'''", "O##P~`"]
        for string in strings:
            with self.subTest(string=string):
                try:
                    dialect = clevercsv.Sniffer().sniff(string)
                except clevercsv.exceptions.Error:
                    pass
