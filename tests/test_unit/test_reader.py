# -*- coding: utf-8 -*-

"""
Unit tests for the CSV reader.

Author: Gertjan van den Burg

"""

import csv
import json
import unittest

from io import StringIO

from typing import Any
from typing import Iterable
from typing import Iterator
from typing import List

import clevercsv


class ReaderTestCase(unittest.TestCase):
    def _read_test(
        self, input: Iterable[str], expect: List[List[str]], **kwargs: Any
    ) -> None:
        reader = clevercsv.reader(input, **kwargs)
        result = list(reader)
        self.assertEqual(result, expect)

    def test_read_oddinputs(self) -> None:
        self._read_test([], [])
        self._read_test([""], [[]])
        self.assertRaises(
            clevercsv.Error, self._read_test, ['"ab"c'], None, strict=1
        )
        self.assertRaises(
            clevercsv.Error, self._read_test, ["ab\0c"], None, strict=1
        )
        # This commented test doesn't make sense for us, because we assert that
        # a field is only a quoted field if it begins *and* ends with a quote
        # character (except for the last field of a file, which only needs to
        # end in a quotechar if we're not strict).
        # self._read_test(['"ab"c'], [["abc"]], doublequote=0)
        self.assertRaises(clevercsv.Error, self._read_test, [b"ab\0c"], None)

    def test_read_eol(self) -> None:
        self._read_test(["a,b"], [["a", "b"]])
        self._read_test(["a,b\n"], [["a", "b"]])
        self._read_test(["a,b\r\n"], [["a", "b"]])
        self._read_test(["a,b\r"], [["a", "b"]])
        # these tests from CPython don't apply for now.
        self.assertRaises(clevercsv.Error, self._read_test, ["a,b\rc,d"], [])
        self.assertRaises(clevercsv.Error, self._read_test, ["a,b\rc,d"], [])
        self.assertRaises(clevercsv.Error, self._read_test, ["a,b\rc,d"], [])

    def test_read_eof(self) -> None:
        self._read_test(['a,"'], [["a", ""]])
        self._read_test(['"a'], [["a"]])
        # we're not using escape characters in the same way.
        # self._read_test("^", [["\n"]], escapechar="^")

    def test_read_escape(self) -> None:
        # we don't drop the escapechar if it serves no purpose
        # so instead of this:
        # self._read_test("a,\\b,c", [["a", "b", "c"]], escapechar="\\")
        # we do this:
        self._read_test(["a,\\b,c"], [["a", "\\b", "c"]], escapechar="\\")
        self._read_test(["a,b\\,c"], [["a", "b,c"]], escapechar="\\")
        self._read_test(['a,"b,c\\""'], [["a", 'b,c"']], escapechar="\\")
        # the next test also differs from Python
        self._read_test(['a,"b,c"\\'], [["a", "b,c"]], escapechar="\\")

    def test_read_bigfield(self) -> None:
        limit = clevercsv.field_size_limit()
        try:
            size = 500
            bigstring = "X" * size
            bigline = "%s,%s" % (bigstring, bigstring)
            self._read_test([bigline], [[bigstring, bigstring]])
            clevercsv.field_size_limit(size)
            self._read_test([bigline], [[bigstring, bigstring]])
            self.assertEqual(clevercsv.field_size_limit(), size)
            clevercsv.field_size_limit(size=-1)
            self.assertRaises(clevercsv.Error, self._read_test, [bigline], [])
            self.assertRaises(TypeError, clevercsv.field_size_limit, None)
            self.assertRaises(TypeError, clevercsv.field_size_limit, 1, None)
        finally:
            clevercsv.field_size_limit(limit)

    def test_read_linenum(self) -> None:
        r = clevercsv.reader(["line,1", "line,2", "line,3"])
        self.assertEqual(r.line_num, 0)
        self.assertEqual(next(r), ["line", "1"])
        self.assertEqual(r.line_num, 1)
        self.assertEqual(next(r), ["line", "2"])
        self.assertEqual(r.line_num, 2)
        self.assertEqual(next(r), ["line", "3"])
        self.assertEqual(r.line_num, 3)
        self.assertRaises(StopIteration, next, r)
        self.assertEqual(r.line_num, 3)

    def test_with_gen(self) -> None:
        def gen(x: Iterable[str]) -> Iterator[str]:
            for line in x:
                yield line

        r = clevercsv.reader(gen(["line,1", "line,2", "line,3"]))
        self.assertEqual(next(r), ["line", "1"])
        self.assertEqual(next(r), ["line", "2"])
        self.assertEqual(next(r), ["line", "3"])

    def test_simple(self) -> None:
        self._read_test(
            ["A,B,C,D,E"],
            [["A", "B", "C", "D", "E"]],
            delimiter=",",
            quotechar='"',
        )
        self._read_test(
            ["A,B,C,D,E"],
            [["A", "B", "C", "D", "E"]],
            delimiter=",",
            quotechar="",
        )
        self._read_test(["A,B,C,D,E"], [["A,B,C,D,E"]], delimiter="")
        self._read_test(
            ['A,"B",C,D,E'],
            [["A", "B", "C", "D", "E"]],
            delimiter=",",
            quotechar='"',
        )
        self._read_test(
            ['A,"B,C",D,E'],
            [["A", "B,C", "D", "E"]],
            delimiter=",",
            quotechar='"',
        )
        self._read_test(
            ['A,"B,C",D,E'],
            [["A", '"B', 'C"', "D", "E"]],
            delimiter=",",
            quotechar="",
        )
        self._read_test(
            ['"A","B","C",,,,'],
            [['"A"', '"B"', '"C"', "", "", "", ""]],
            delimiter=",",
            quotechar="",
        )

    def test_no_delim(self) -> None:
        self._read_test(
            ['A"B"C', 'A"B""C""D"'],
            [['A"B"C'], ['A"B""C""D"']],
            delimiter="",
            quotechar="",
        )
        self._read_test(
            ['A"B\r\nB"C', 'D"E"F', "G"],
            [['A"B\r\nB"C'], ['D"E"F'], ["G"]],
            delimiter="",
            quotechar='"',
        )
        self._read_test(
            ['A"B\nB"C', 'D"E"F', "G"],
            [['A"B\nB"C'], ['D"E"F'], ["G"]],
            delimiter="",
            quotechar='"',
        )
        self._read_test(
            ['A"B\nB\rB"C', 'D"E"F', "G"],
            [['A"B\nB\rB"C'], ['D"E"F'], ["G"]],
            delimiter="",
            quotechar='"',
        )

    def test_github_issue_130(self) -> None:
        # fmt: off
        data = """sku,features,attributes
22221,"[{""key"":""heel_height"",""value"":""Ulttra High (4\\""+)""}]","11,room"
"""
        # fmt: on

        # NOTE we set the escapechar to None to correctly carry over the `\`
        # escape character
        rows_csv = list(
            csv.reader(
                StringIO(data), delimiter=",", quotechar='"', escapechar=None
            )
        )
        expected = [
            [
                "sku",
                "features",
                "attributes",
            ],
            [
                "22221",
                '[{"key":"heel_height","value":"Ulttra High (4\\"+)"}]',
                "11,room",
            ],
        ]
        self.assertSequenceEqual(expected, rows_csv)

        rows_clevercsv = list(
            clevercsv.reader(
                StringIO(data), delimiter=",", quotechar='"', escapechar=""
            )
        )
        self.assertSequenceEqual(expected, rows_clevercsv)

        # Ensure we can parse the JSON as intended.
        cell = json.loads(expected[1][1])
        self.assertEqual(
            cell, [{"key": "heel_height", "value": 'Ulttra High (4"+)'}]
        )


if __name__ == "__main__":
    unittest.main()
