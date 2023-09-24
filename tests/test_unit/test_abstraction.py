# -*- coding: utf-8 -*-

"""
Unit tests for making abstractions

"""

import gzip
import json
import unittest

from pathlib import Path

from typing import Any
from typing import Dict
from typing import List

from clevercsv.cabstraction import c_merge_with_quotechar
from clevercsv.detect_pattern import base_abstraction
from clevercsv.detect_pattern import fill_empties
from clevercsv.detect_pattern import strip_trailing


class AbstractionTestCase(unittest.TestCase):
    def setUp(self) -> None:
        here = Path(__file__)
        this_dir = here.parent
        data_dir = this_dir / "data"
        testcases_file = data_dir / "abstraction_testcases.json.gz"
        if not testcases_file.exists():
            self._cases = []
        else:
            self._cases = self._load_cases(testcases_file)

    @staticmethod
    def _load_cases(filename: Path) -> List[Dict[str, Any]]:
        cases = []
        with gzip.open(filename, "rt", newline="", encoding="utf-8") as fp:
            for line in fp:
                cases.append(json.loads(line))
        return cases

    def test_abstraction_multi(self) -> None:
        if not self._cases:
            self.skipTest("no abstraction test cases found")

        for case in self._cases:
            content = case["content"]
            dialect = case["dialect"]

            exp_base = case["base_abstraction"]
            exp_merge = case["after_merge_with_quotechar"]
            exp_empties = case["after_fill_empties"]
            exp_trailing = case["after_strip_trailing"]
            with self.subTest(name=case["name"], kind="base"):
                base = base_abstraction(
                    content,
                    dialect["delimiter"],
                    dialect["quotechar"],
                    dialect["escapechar"],
                )
                self.assertEqual(base, exp_base)

            with self.subTest(name=case["name"], kind="merge"):
                merge = c_merge_with_quotechar(base)
                self.assertEqual(merge, exp_merge)

            with self.subTest(name=case["name"], kind="empties"):
                empties = fill_empties(merge)
                self.assertEqual(empties, exp_empties)

            with self.subTest(name=case["name"], kind="trailing"):
                trailing = strip_trailing(empties)
                self.assertEqual(trailing, exp_trailing)


if __name__ == "__main__":
    unittest.main()
