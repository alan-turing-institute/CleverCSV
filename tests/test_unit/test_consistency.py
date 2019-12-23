# -*- coding: utf-8 -*-

"""
Unit test for consistency score

Author: G.J.J. van den Burg

"""

import unittest

from clevercsv.consistency import get_best_set
from clevercsv.dialect import SimpleDialect


class ConsistencyTestCase(unittest.TestCase):
    def test_get_best_set_1(self):
        scores = {
            SimpleDialect(",", None, None): {"Q": 1.0},
            SimpleDialect(";", None, None): {"Q": None},
            SimpleDialect("|", None, None): {"Q": 2.0},
        }
        H = get_best_set(scores)
        self.assertEqual(H, set([SimpleDialect("|", None, None)]))

    def test_get_best_set_2(self):
        scores = {
            SimpleDialect(";", None, None): {"Q": None},
            SimpleDialect(",", None, None): {"Q": 1.0},
            SimpleDialect("|", None, None): {"Q": 2.0},
        }
        H = get_best_set(scores)
        self.assertEqual(H, set([SimpleDialect("|", None, None)]))
