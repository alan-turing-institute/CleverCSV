# -*- coding: utf-8 -*-

"""
Unit test for consistency score

Author: G.J.J. van den Burg

"""

import unittest

from clevercsv.consistency import ConsistencyDetector
from clevercsv.consistency import ConsistencyScore
from clevercsv.dialect import SimpleDialect


class ConsistencyTestCase(unittest.TestCase):
    def test_get_best_set_1(self) -> None:
        scores = {
            SimpleDialect(",", None, None): ConsistencyScore(P=1, T=1, Q=1),
            SimpleDialect(";", None, None): ConsistencyScore(
                P=1, T=None, Q=None
            ),
            SimpleDialect("|", None, None): ConsistencyScore(P=2, T=1, Q=2),
        }
        H = ConsistencyDetector.get_best_dialects(scores)
        self.assertEqual(H, [SimpleDialect("|", None, None)])
