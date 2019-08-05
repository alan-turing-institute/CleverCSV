# -*- coding: utf-8 -*-

"""
Unit tests for the CCSV write module.

Author: Gertjan van den Burg

"""


import clevercsv
import tempfile
import unittest

from clevercsv.dialect import SimpleDialect


class WriterTestCase(unittest.TestCase):
    def writerAssertEqual(self, input, expected_result):
        with tempfile.TemporaryFile("w+", newline="") as fileobj:
            writer = clevercsv.writer(fileobj, dialect=self.dialect)
            writer.writerows(input)
            fileobj.seek(0)
            self.assertEqual(fileobj.read(), expected_result)

    def _write_test(self, fields, expect, **kwargs):
        with tempfile.TemporaryFile("w+", newline="") as fileobj:
            writer = clevercsv.writer(fileobj, **kwargs)
            writer.writerow(fields)
            fileobj.seek(0)
            self.assertEqual(
                fileobj.read(), expect + writer.dialect.lineterminator
            )

    def _write_error_test(self, exc, fields, **kwargs):
        with tempfile.TemporaryFile("w+", newline="") as fileobj:
            writer = clevercsv.writer(fileobj, **kwargs)
            with self.assertRaises(exc):
                writer.writerow(fields)
            fileobj.seek(0)
            self.assertEqual(fileobj.read(), "")

    def test_write_arg_valid(self):
        self._write_error_test(clevercsv.Error, None)
        self._write_test((), "")
        self._write_test([None], '""')
        self._write_error_test(
            clevercsv.Error, [None], quoting=clevercsv.QUOTE_NONE
        )
        # Check that exceptions are passed up the chain
        class BadList:
            def __len__(self):
                return 10

            def __getitem__(self, i):
                if i > 2:
                    raise OSError

        self._write_error_test(OSError, BadList())

        class BadItem:
            def __str__(self):
                raise OSError

        self._write_error_test(OSError, [BadItem()])

    def test_write_bigfield(self):
        bigstring = "X" * 50000
        self._write_test(
            [bigstring, bigstring], "%s,%s" % (bigstring, bigstring)
        )

    def test_write_quoting(self):
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

    def test_write_simpledialect(self):
        self._write_test(
            ["a", 1, "p,q"],
            "a,1,|p,q|",
            dialect=SimpleDialect(delimiter=",", quotechar="|", escapechar=""),
        )


if __name__ == "__main__":
    unittest.main()
