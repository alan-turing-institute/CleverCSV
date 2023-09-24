# -*- coding: utf-8 -*-

"""
Unit tests for the CCSV write module.

Author: Gertjan van den Burg

"""


import csv
import tempfile
import unittest

from typing import Any
from typing import Iterable
from typing import Type

import clevercsv

from clevercsv.dialect import SimpleDialect


class WriterTestCase(unittest.TestCase):
    def _write_test(
        self, fields: Iterable[Any], expect: str, **kwargs: Any
    ) -> None:
        with tempfile.TemporaryFile("w+", newline="", prefix="ccsv_") as fp:
            writer = clevercsv.writer(fp, **kwargs)
            writer.writerow(fields)
            fp.seek(0)
            self.assertEqual(fp.read(), expect + writer.dialect.lineterminator)

    def _write_error_test(
        self, exc: Type[Exception], fields: Any, **kwargs: Any
    ) -> None:
        with tempfile.TemporaryFile("w+", newline="", prefix="ccsv_") as fp:
            writer = clevercsv.writer(fp, **kwargs)
            with self.assertRaises(exc):
                writer.writerow(fields)
            fp.seek(0)
            self.assertEqual(fp.read(), "")

    def test_write_arg_valid(self) -> None:
        self._write_error_test(clevercsv.Error, None)
        self._write_test((), "")
        self._write_test([None], '""')
        self._write_error_test(
            clevercsv.Error, [None], quoting=clevercsv.QUOTE_NONE
        )

        # Check that exceptions are passed up the chain
        class BadList:
            def __len__(self) -> int:
                return 10

            def __getitem__(self, i: int) -> None:
                if i > 2:
                    raise OSError

        self._write_error_test(OSError, BadList())

        class BadItem:
            def __str__(self) -> str:
                raise OSError

        self._write_error_test(OSError, [BadItem()])

    def test_write_bigfield(self) -> None:
        bigstring = "X" * 50000
        self._write_test(
            [bigstring, bigstring], "%s,%s" % (bigstring, bigstring)
        )

    def test_write_quoting(self) -> None:
        self._write_test(["a", 1, "p,q"], 'a,1,"p,q"')
        self._write_error_test(
            clevercsv.Error, ["a", 1, "p,q"], quoting=clevercsv.QUOTE_NONE
        )
        self._write_test(
            ["a", 1, "p,q"], 'a,1,"p,q"', quoting=clevercsv.QUOTE_MINIMAL
        )
        self._write_test(
            ["a", 1, "p,q"], '"a",1,"p,q"', quoting=clevercsv.QUOTE_NONNUMERIC
        )
        self._write_test(
            ["a", 1, "p,q"], '"a","1","p,q"', quoting=clevercsv.QUOTE_ALL
        )
        self._write_test(
            ["a\nb", 1], '"a\nb","1"', quoting=clevercsv.QUOTE_ALL
        )

    def test_write_simpledialect(self) -> None:
        self._write_test(
            ["a", 1, "p,q"],
            "a,1,|p,q|",
            dialect=SimpleDialect(delimiter=",", quotechar="|", escapechar=""),
        )

    def test_write_csv_dialect(self) -> None:
        self._write_test(
            ["a", 1, "p,q"],
            'a,1,"p,q"',
            dialect="excel",
        )
        self._write_test(
            ["a", 1, "p,q"],
            '"a","1","p,q"',
            dialect=csv.unix_dialect,
        )
        self._write_test(
            [1, 2, 3],
            "1\t2\t3",
            dialect=clevercsv.excel_tab,
        )


if __name__ == "__main__":
    unittest.main()
