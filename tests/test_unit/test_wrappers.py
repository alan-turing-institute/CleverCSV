# -*- coding: utf-8 -*-

"""
Unit tests for the wrappers

Author: Gertjan van den Burg

"""

import unittest
import tempfile
import pandas as pd
import os

from ccsv import wrappers, writer
from ccsv.dialect import SimpleDialect


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
