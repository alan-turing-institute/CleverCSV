# -*- coding: utf-8 -*-

"""Unit tests for encoding detection

Author: G.J.J. van den Burg
License: See the LICENSE file.

This file is part of CleverCSV.

"""

import os
import tempfile
import unittest

from dataclasses import dataclass

from typing import Any
from typing import List

from clevercsv._optional import import_optional_dependency
from clevercsv._types import AnyPath
from clevercsv.encoding import get_encoding
from clevercsv.write import writer


class EncodingTestCase(unittest.TestCase):
    @dataclass
    class Instance:
        table: List[List[Any]]
        encoding: str
        cchardet_encoding: str

    cases: List[Instance] = [
        Instance(
            table=[["Å", "B", "C"], [1, 2, 3], [4, 5, 6]],
            encoding="ISO-8859-1",
            cchardet_encoding="WINDOWS-1252",
        ),
        Instance(
            table=[["A", "B", "C"], [1, 2, 3], [4, 5, 6]],
            encoding="ascii",
            cchardet_encoding="ASCII",
        ),
        Instance(
            table=[["亜唖", "娃阿", "哀愛"], [1, 2, 3], ["挨", "姶", "葵"]],
            encoding="ISO-2022-JP",
            cchardet_encoding="ISO-2022-JP",
        ),
    ]

    def setUp(self) -> None:
        self._tmpfiles: List[AnyPath] = []

    def tearDown(self) -> None:
        for f in self._tmpfiles:
            os.unlink(f)

    def _build_file(self, table: List[List[str]], encoding: str) -> str:
        tmpfd, tmpfname = tempfile.mkstemp(
            prefix="ccsv_",
            suffix=".csv",
        )
        tmpfp = os.fdopen(tmpfd, "w", newline=None, encoding=encoding)
        w = writer(tmpfp, dialect="excel")
        w.writerows(table)
        tmpfp.close()
        self._tmpfiles.append(tmpfname)
        return tmpfname

    def test_encoding_chardet(self) -> None:
        for case in self.cases:
            table = case.table
            encoding = case.encoding
            with self.subTest(encoding=encoding):
                tmpfname = self._build_file(table, encoding)
                detected = get_encoding(tmpfname, try_cchardet=False)
                self.assertEqual(encoding, detected)

    def test_encoding_cchardet(self) -> None:
        try:
            _ = import_optional_dependency("cchardet")
        except ImportError:
            self.skipTest("Failed to import cchardet, skipping this test")

        for case in self.cases:
            table = case.table
            encoding = case.encoding
            with self.subTest(encoding=encoding):
                out_encoding = case.cchardet_encoding
                tmpfname = self._build_file(table, encoding)
                detected = get_encoding(tmpfname, try_cchardet=True)
                self.assertEqual(out_encoding, detected)


if __name__ == "__main__":
    unittest.main()
