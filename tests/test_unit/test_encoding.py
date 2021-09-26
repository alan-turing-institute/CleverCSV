# -*- coding: utf-8 -*-

"""Unit tests for encoding detection

Author: G.J.J. van den Burg
License: See the LICENSE file.

This file is part of CleverCSV.

"""

import os
import tempfile
import unittest

from clevercsv.encoding import get_encoding
from clevercsv.write import writer


class EncodingTestCase(unittest.TestCase):
    def setUp(self):
        self._tmpfiles = []

    def tearDown(self):
        for f in self._tmpfiles:
            os.unlink(f)

    def _build_file(self, table, encoding):
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

    def test_encoding_1(self):
        table = [["Å", "B", "C"], [1, 2, 3], [4, 5, 6]]
        encoding = "ISO-8859-1"
        tmpfname = self._build_file(table, encoding)

        # Test using chardet
        detected = get_encoding(tmpfname, try_cchardet=False)
        self.assertEqual(encoding, detected)

        # Test using cChardet
        detected = get_encoding(tmpfname, try_cchardet=True)
        self.assertEqual("WINDOWS-1252", detected)

    def test_encoding_2(self):
        table = [["A", "B", "C"], [1, 2, 3], [4, 5, 6]]
        encoding = "ascii"
        tmpfname = self._build_file(table, encoding)

        # Test using chardet
        detected = get_encoding(tmpfname, try_cchardet=False)
        self.assertEqual(encoding, detected)

        # Test using cChardet
        detected = get_encoding(tmpfname, try_cchardet=True)
        self.assertEqual("ASCII", detected)

    def test_encoding_3(self):
        table = [["亜唖", "娃阿", "哀愛"], [1, 2, 3], ["挨", "姶", "葵"]]
        encoding = "ISO-2022-JP"
        tmpfname = self._build_file(table, encoding)

        # Test using chardet
        detected = get_encoding(tmpfname)
        self.assertEqual(encoding, detected)

        # Test using cChardet
        detected = get_encoding(tmpfname, try_cchardet=True)
        self.assertEqual(encoding, detected)


if __name__ == "__main__":
    unittest.main()
