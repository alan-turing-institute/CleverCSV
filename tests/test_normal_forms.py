# -*- coding: utf-8 -*-

"""
Unit tests for the normal form detection.

Author: Gertjan van den Burg

"""

import unittest

from ccsv.dialect import SimpleDialect
from ccsv.normal_form import is_form_1


class NormalFormTestCase(unittest.TestCase):
    def test_form_1(self):
        self.assertTrue(
            is_form_1(
                '"A","B","C"',
                SimpleDialect(delimiter=",", quotechar='"', escapechar=""),
            )
        )
        self.assertTrue(
            is_form_1(
                '"A","B"\n"C","D"\n',
                SimpleDialect(delimiter=",", quotechar='"', escapechar=""),
            )
        )
        self.assertFalse(
            is_form_1(
                '"A","","C"',
                SimpleDialect(delimiter=",", quotechar='"', escapechar=""),
            )
        )
        self.assertFalse(
            is_form_1(
                '"A",,"C"',
                SimpleDialect(delimiter=",", quotechar='"', escapechar=""),
            )
        )
        self.assertFalse(
            is_form_1(
                '"A"\n"C"\n',
                SimpleDialect(delimiter=",", quotechar='"', escapechar=""),
            )
        )
