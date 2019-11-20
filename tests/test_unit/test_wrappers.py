# -*- coding: utf-8 -*-

"""
Unit tests for the wrappers

Author: Gertjan van den Burg

"""

import os
import pandas as pd
import tempfile
import unittest

from clevercsv import wrappers, writer
from clevercsv.dialect import SimpleDialect
from clevercsv.exceptions import NoDetectionResult


class WrappersTestCase(unittest.TestCase):
    def _df_test(self, table, dialect):
        tmpfd, tmpfname = tempfile.mkstemp()
        tmpid = os.fdopen(tmpfd, "w")
        w = writer(tmpid, dialect=dialect)
        w.writerows(table)
        tmpid.close()

        exp_df = pd.DataFrame.from_records(table[1:], columns=table[0])
        df = wrappers.csv2df(tmpfname)

        try:
            self.assertTrue(df.equals(exp_df))
        finally:
            os.unlink(tmpfname)

    def _read_test(self, table, dialect):
        tmpfd, tmpfname = tempfile.mkstemp()
        tmpid = os.fdopen(tmpfd, "w")
        w = writer(tmpid, dialect=dialect)
        w.writerows(table)
        tmpid.close()

        exp = [list(map(str, r)) for r in table]
        try:
            self.assertEqual(exp, wrappers.read_csv(tmpfname))
        finally:
            os.unlink(tmpfname)

    def _read_test_rows(self, rows, expected):
        contents = "\n".join(rows)
        tmpfd, tmpfname = tempfile.mkstemp()
        tmpid = os.fdopen(tmpfd, "w")
        tmpid.write(contents)
        tmpid.close()

        try:
            self.assertEqual(expected, wrappers.read_csv(tmpfname))
        finally:
            os.unlink(tmpfname)

    def test_csv2df(self):
        table = [["A", "B", "C"], [1, 2, 3], [4, 5, 6]]
        dialect = SimpleDialect(delimiter=";", quotechar="", escapechar="")
        with self.subTest(name="simple"):
            self._df_test(table, dialect)

        table = [["A,0", "B", "C"], [1, 2, 3], [4, 5, 6]]
        dialect = SimpleDialect(delimiter=",", quotechar="", escapechar="\\")
        with self.subTest(name="escaped"):
            self._df_test(table, dialect)

        table = [["A,0", "B", "C"], [1, 2, 3], [4, 5, 6]]
        dialect = SimpleDialect(delimiter=",", quotechar='"', escapechar="")
        with self.subTest(name="quoted"):
            self._df_test(table, dialect)

        table = [['a"A,0"b', "B", "C"], [1, 2, 3], [4, 5, 6]]
        dialect = SimpleDialect(delimiter=",", quotechar='"', escapechar="")
        with self.subTest(name="double"):
            self._df_test(table, dialect)

    def test_read_csv(self):
        table = [["A", "B", "C"], [1, 2, 3], [4, 5, 6]]
        dialect = SimpleDialect(delimiter=";", quotechar="", escapechar="")
        with self.subTest(name="simple"):
            self._read_test(table, dialect)

        table = [["A,0", "B", "C"], [1, 2, 3], [4, 5, 6]]
        dialect = SimpleDialect(delimiter=",", quotechar="", escapechar="\\")
        with self.subTest(name="escaped"):
            self._read_test(table, dialect)

        table = [["A,0", "B", "C"], [1, 2, 3], [4, 5, 6]]
        dialect = SimpleDialect(delimiter=",", quotechar='"', escapechar="")
        with self.subTest(name="quoted"):
            self._read_test(table, dialect)

        table = [['a"A,0"b', "B", "C"], [1, 2, 3], [4, 5, 6]]
        dialect = SimpleDialect(delimiter=",", quotechar='"', escapechar="")
        with self.subTest(name="double"):
            self._read_test(table, dialect)

        rows = ['1,"AA"', '2,"BB"', '3,"CC"']
        exp = [["1", "AA"], ["2", "BB"], ["3", "CC"]]
        with self.subTest(name="rowtest"):
            self._read_test_rows(rows, exp)

        # This raises a NoDetectionResult due to the spacing after the
        # delimiter, which confuses the detection algorithm. Support for
        # detecting 'skipinitialspace' should fix this problem.
        rows = ['1, "AA"', '2, "BB"', '3, "CC"']
        exp = [["1", "AA"], ["2", "BB"], ["3", "CC"]]
        with self.subTest(name="raises2"):
            with self.assertRaises(NoDetectionResult):
                self._read_test_rows(rows, exp)

    def _write_test(self, table, expected, dialect="excel", transpose=False):
        tmpfd, tmpfname = tempfile.mkstemp()
        wrappers.write_table(
            table, tmpfname, dialect=dialect, transpose=transpose
        )
        with open(tmpfname, "r") as fp:
            data = fp.read()

        try:
            self.assertEqual(data, expected)
        finally:
            os.close(tmpfd)
            os.unlink(tmpfname)

    def test_write(self):
        table = [["A", "B,C", "D"], [1, 2, 3], [4, 5, 6]]
        exp = 'A,"B,C",D\n1,2,3\n4,5,6\n'
        with self.subTest(name="default"):
            self._write_test(table, exp)

        dialect = SimpleDialect(delimiter=";", quotechar="", escapechar="")
        exp = "A;B,C;D\n1;2;3\n4;5;6\n"
        with self.subTest(name="dialect"):
            self._write_test(table, exp, dialect=dialect)

        exp = "A;1;4\nB,C;2;5\nD;3;6\n"
        with self.subTest(name="transposed"):
            self._write_test(table, exp, dialect=dialect, transpose=True)

        table[2].append(8)
        with self.assertRaises(ValueError):
            self._write_test(table, '')
