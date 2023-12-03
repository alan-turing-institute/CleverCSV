# -*- coding: utf-8 -*-

"""
Unit tests for the console application.

Author: Gertjan van den Burg
"""

import json
import os
import tempfile
import unittest

from typing import Any
from typing import List
from typing import Optional

from wilderness import Tester

from clevercsv import __version__
from clevercsv._types import _DialectLike
from clevercsv.console import build_application
from clevercsv.dialect import SimpleDialect
from clevercsv.encoding import get_encoding
from clevercsv.write import writer

TableType = List[List[Any]]


class ConsoleTestCase(unittest.TestCase):
    def _build_file(
        self,
        table: TableType,
        dialect: _DialectLike,
        encoding: Optional[str] = None,
        newline: Optional[str] = None,
    ) -> str:
        tmpfd, tmpfname = tempfile.mkstemp(
            prefix="ccsv_",
            suffix=".csv",
        )
        tmpid = os.fdopen(tmpfd, "w", newline=newline, encoding=encoding)
        w = writer(tmpid, dialect=dialect)
        w.writerows(table)
        tmpid.close()
        return tmpfname

    def _detect_test_wrap(
        self, table: TableType, dialect: _DialectLike
    ) -> None:
        tmpfname = self._build_file(table, dialect)
        exp = "Detected: " + str(dialect)

        application = build_application()
        tester = Tester(application)
        tester.test_command("detect", [tmpfname])

        try:
            stdout = tester.get_stdout()
            self.assertIsNotNone(stdout)
            assert stdout is not None
            output = stdout.strip()
            self.assertEqual(exp, output)
        finally:
            os.unlink(tmpfname)

    def test_detect_base(self) -> None:
        table: TableType = [["A", "B", "C"], [1, 2, 3], [4, 5, 6]]
        dialect = SimpleDialect(delimiter=";", quotechar="", escapechar="")
        with self.subTest(name="simple"):
            self._detect_test_wrap(table, dialect)

        table = [["A,0", "B", "C"], [1, 2, 3], [4, 5, 6]]
        dialect = SimpleDialect(delimiter=",", quotechar="", escapechar="\\")
        with self.subTest(name="escaped"):
            self._detect_test_wrap(table, dialect)

        table = [["A,0", "B", "C"], [1, 2, 3], [4, 5, 6]]
        dialect = SimpleDialect(delimiter=",", quotechar='"', escapechar="")
        with self.subTest(name="quoted"):
            self._detect_test_wrap(table, dialect)

        table = [['a"A,0"b', "B", "C"], [1, 2, 3], [4, 5, 6]]
        dialect = SimpleDialect(delimiter=",", quotechar='"', escapechar="")
        with self.subTest(name="double"):
            self._detect_test_wrap(table, dialect)

    def test_detect_opts_1(self) -> None:
        table: TableType = [["A", "B", "C"], [1, 2, 3], [4, 5, 6]]
        dialect = SimpleDialect(delimiter=";", quotechar="", escapechar="")
        encoding = "windows-1252"
        tmpfname = self._build_file(table, dialect, encoding=encoding)

        application = build_application()
        tester = Tester(application)
        tester.test_command("detect", ["--encoding", encoding, tmpfname])

        exp = "Detected: " + str(dialect)

        try:
            stdout = tester.get_stdout()
            self.assertIsNotNone(stdout)
            assert stdout is not None
            output = stdout.strip()
            self.assertEqual(exp, output)
        finally:
            os.unlink(tmpfname)

    def test_detect_opts_2(self) -> None:
        table: TableType = [["A", "B", "C"], [1, 2, 3], [4, 5, 6]]
        dialect = SimpleDialect(delimiter=";", quotechar="", escapechar="")
        tmpfname = self._build_file(table, dialect)

        application = build_application()
        tester = Tester(application)
        tester.test_command("detect", ["--num-chars", "5", tmpfname])

        exp = "Detected: " + str(dialect)

        try:
            stdout = tester.get_stdout()
            self.assertIsNotNone(stdout)
            assert stdout is not None
            output = stdout.strip()
            self.assertEqual(exp, output)
        finally:
            os.unlink(tmpfname)

    def test_detect_opts_3(self) -> None:
        table: TableType = [["A", "B", "C"], [1, 2, 3], [4, 5, 6]]
        dialect = SimpleDialect(delimiter=";", quotechar="", escapechar="")
        tmpfname = self._build_file(table, dialect)

        application = build_application()
        tester = Tester(application)
        tester.test_command("detect", ["--plain", tmpfname])

        exp = """\
delimiter = ;
quotechar =
escapechar ="""
        try:
            stdout = tester.get_stdout()
            self.assertIsNotNone(stdout)
            assert stdout is not None
            output = stdout.strip()
            self.assertEqual(exp, output)
        finally:
            os.unlink(tmpfname)

    def test_detect_opts_4(self) -> None:
        table: TableType = [["A", "B", "C"], [1, 2, 3], [4, 5, 6]]
        dialect = SimpleDialect(delimiter=";", quotechar="", escapechar="")
        tmpfname = self._build_file(table, dialect)

        application = build_application()
        tester = Tester(application)
        tester.test_command("detect", ["--json", "--add-runtime", tmpfname])

        try:
            stdout = tester.get_stdout()
            self.assertIsNotNone(stdout)
            assert stdout is not None
            output = stdout.strip()
            data = json.loads(output)
            self.assertEqual(data["delimiter"], ";")
            self.assertEqual(data["quotechar"], "")
            self.assertEqual(data["escapechar"], "")
            self.assertIsInstance(data["runtime"], float)
        finally:
            os.unlink(tmpfname)

    def test_code_1(self) -> None:
        table: TableType = [["A", "B", "C"], [1, 2, 3], [4, 5, 6]]
        dialect = SimpleDialect(delimiter=";", quotechar="", escapechar="")

        tmpfname = self._build_file(table, dialect)

        application = build_application()
        tester = Tester(application)
        tester.test_command("code", [tmpfname])

        # for chardet
        exp_1 = f"""\

# Code generated with CleverCSV version {__version__}

import clevercsv

with open("{tmpfname}", "r", newline="", encoding="ascii") as fp:
    reader = clevercsv.reader(fp, delimiter=";", quotechar="", escapechar="")
    rows = list(reader)

"""

        # for cChardet
        exp_2 = f"""\

# Code generated with CleverCSV version {__version__}

import clevercsv

with open("{tmpfname}", "r", newline="", encoding="ASCII") as fp:
    reader = clevercsv.reader(fp, delimiter=";", quotechar="", escapechar="")
    rows = list(reader)

"""
        try:
            output = tester.get_stdout()
            self.assertIn(output, [exp_1, exp_2])
        finally:
            os.unlink(tmpfname)

    def test_code_2(self) -> None:
        table: TableType = [["A", "B", "C"], [1, 2, 3], [4, 5, 6]]
        dialect = SimpleDialect(delimiter=";", quotechar="", escapechar="")
        tmpfname = self._build_file(table, dialect)

        application = build_application()
        tester = Tester(application)
        tester.test_command("code", ["-p", tmpfname])

        exp = f"""\

# Code generated with CleverCSV version {__version__}

import clevercsv

df = clevercsv.read_dataframe("{tmpfname}", delimiter=";", quotechar="", escapechar="")

"""
        try:
            output = tester.get_stdout()
            self.assertEqual(exp, output)
        finally:
            os.unlink(tmpfname)

    def test_code_3(self) -> None:
        table: TableType = [["Å", "B", "C"], [1, 2, 3], [4, 5, 6]]
        dialect = SimpleDialect(delimiter=";", quotechar="", escapechar="")
        encoding = "ISO-8859-1"
        tmpfname = self._build_file(table, dialect, encoding=encoding)

        application = build_application()
        tester = Tester(application)
        tester.test_command("code", [tmpfname])

        # for chardet
        exp_1 = f"""\

# Code generated with CleverCSV version {__version__}

import clevercsv

with open("{tmpfname}", "r", newline="", encoding="{encoding}") as fp:
    reader = clevercsv.reader(fp, delimiter=";", quotechar="", escapechar="")
    rows = list(reader)

"""

        # for cChardet
        exp_2 = f"""\

# Code generated with CleverCSV version {__version__}

import clevercsv

with open("{tmpfname}", "r", newline="", encoding="WINDOWS-1252") as fp:
    reader = clevercsv.reader(fp, delimiter=";", quotechar="", escapechar="")
    rows = list(reader)

"""
        try:
            output = tester.get_stdout()
            self.assertIn(output, [exp_1, exp_2])
        finally:
            os.unlink(tmpfname)

    def test_code_4(self) -> None:
        table: TableType = [["Å", "B,D", "C"], [1, 2, 3], [4, 5, 6]]
        dialect = SimpleDialect(delimiter=",", quotechar="", escapechar="\\")
        encoding = "ISO-8859-1"
        tmpfname = self._build_file(table, dialect, encoding=encoding)

        application = build_application()
        tester = Tester(application)
        tester.test_command("code", [tmpfname])

        # for chardet
        exp_1 = f"""\

# Code generated with CleverCSV version {__version__}

import clevercsv

with open("{tmpfname}", "r", newline="", encoding="{encoding}") as fp:
    reader = clevercsv.reader(fp, delimiter=",", quotechar="", escapechar="\\\\")
    rows = list(reader)

"""

        # for cChardet
        exp_2 = f"""\

# Code generated with CleverCSV version {__version__}

import clevercsv

with open("{tmpfname}", "r", newline="", encoding="WINDOWS-1252") as fp:
    reader = clevercsv.reader(fp, delimiter=",", quotechar="", escapechar="\\\\")
    rows = list(reader)

"""
        try:
            output = tester.get_stdout()
            self.assertIn(output, [exp_1, exp_2])
        finally:
            os.unlink(tmpfname)

    def test_code_5(self) -> None:
        table: TableType = [["A", "B", "C"], [1, 2, 3], [4, 5, 6]]
        dialect = SimpleDialect(delimiter="\t", quotechar="", escapechar="")

        tmpfname = self._build_file(table, dialect)

        application = build_application()
        tester = Tester(application)
        tester.test_command("code", [tmpfname])

        # for chardet
        exp_1 = f"""\

# Code generated with CleverCSV version {__version__}

import clevercsv

with open("{tmpfname}", "r", newline="", encoding="ascii") as fp:
    reader = clevercsv.reader(fp, delimiter="\\t", quotechar="", escapechar="")
    rows = list(reader)

"""

        # for cChardet
        exp_2 = f"""\

# Code generated with CleverCSV version {__version__}

import clevercsv

with open("{tmpfname}", "r", newline="", encoding="ASCII") as fp:
    reader = clevercsv.reader(fp, delimiter="\\t", quotechar="", escapechar="")
    rows = list(reader)

"""

        try:
            output = tester.get_stdout()
            self.assertIn(output, [exp_1, exp_2])
        finally:
            os.unlink(tmpfname)

    def test_standardize_1(self) -> None:
        table: TableType = [["A", "B", "C"], [1, 2, 3], [4, 5, 6]]
        dialect = SimpleDialect(delimiter=";", quotechar="", escapechar="")
        tmpfname = self._build_file(table, dialect)

        application = build_application()
        tester = Tester(application)
        tester.test_command("standardize", [tmpfname])

        # Excel format (i.e. RFC4180) *requires* CRLF
        crlf = "\r\n"
        exp = crlf.join(["A,B,C", "1,2,3", "4,5,6"])
        # add line terminator of last row
        exp += crlf
        try:
            output = tester.get_stdout()
            self.assertEqual(exp, output)
        finally:
            os.unlink(tmpfname)

    def test_standardize_2(self) -> None:
        table: TableType = [["A", "B", "C"], [1, 2, 3], [4, 5, 6]]
        dialect = SimpleDialect(delimiter=";", quotechar="", escapechar="")
        tmpfname = self._build_file(table, dialect)

        tmpfd, tmpoutname = tempfile.mkstemp(prefix="ccsv_", suffix=".csv")
        os.close(tmpfd)

        application = build_application()
        tester = Tester(application)
        tester.test_command("standardize", ["-o", tmpoutname, tmpfname])

        # Excel format (i.e. RFC4180) *requires* CRLF
        crlf = "\r\n"
        exp = crlf.join(["A,B,C", "1,2,3", "4,5,6", ""])
        with open(tmpoutname, "r", newline="") as fp:
            output = fp.read()

        try:
            self.assertEqual(exp, output)
        finally:
            os.unlink(tmpfname)
            os.unlink(tmpoutname)

    def test_standardize_3(self) -> None:
        table: TableType = [["A", "B", "C"], [1, 2, 3], [4, 5, 6]]
        dialect = SimpleDialect(delimiter=";", quotechar="", escapechar="")
        tmpfname = self._build_file(table, dialect)

        application = build_application()
        tester = Tester(application)
        tester.test_command("standardize", ["-t", tmpfname])

        # Excel format (i.e. RFC4180) *requires* CRLF
        crlf = "\r\n"
        exp = crlf.join(["A,1,4", "B,2,5", "C,3,6"])
        # add line terminator of last row
        exp += crlf

        try:
            output = tester.get_stdout()
            self.assertEqual(exp, output)
        finally:
            os.unlink(tmpfname)

    def test_standardize_in_place(self) -> None:
        table: TableType = [["A", "B", "C"], [1, 2, 3], [4, 5, 6]]
        dialect = SimpleDialect(delimiter=";", quotechar="", escapechar="")
        tmpfname = self._build_file(table, dialect)

        application = build_application()
        tester = Tester(application)
        tester.test_command("standardize", ["-i", tmpfname])

        self.assertEqual(tester.get_return_code(), 2)

        # Excel format (i.e. RFC4180) *requires* CRLF
        crlf = "\r\n"
        exp = crlf.join(["A,B,C", "1,2,3", "4,5,6"])
        # add line terminator of last row
        exp += crlf

        try:
            with open(tmpfname, "r", newline="") as fp:
                contents = fp.read()
            self.assertEqual(exp, contents)
        finally:
            os.unlink(tmpfname)

    def test_standardize_in_place_noop(self) -> None:
        table: TableType = [["A", "B", "C"], [1, 2, 3], [4, 5, 6]]
        dialect = "excel"
        tmpfname = self._build_file(table, dialect, newline="")

        application = build_application()
        tester = Tester(application)
        tester.test_command("standardize", ["-i", tmpfname])

        self.assertEqual(tester.get_return_code(), 0)

        # Excel format (i.e. RFC4180) *requires* CRLF
        crlf = "\r\n"
        exp = crlf.join(["A,B,C", "1,2,3", "4,5,6"])
        # add line terminator of last row
        exp += crlf

        try:
            with open(tmpfname, "r", newline="") as fp:
                contents = fp.read()
            self.assertEqual(exp, contents)
        finally:
            os.unlink(tmpfname)

    def test_standardize_multi(self) -> None:
        table: TableType = [
            ["A", "B", "C"],
            [1, 2, 3],
            [4, 5, 6],
        ]
        dialects = ["excel", "unix", "excel-tab"]
        tmpfnames = [self._build_file(table, D, newline="") for D in dialects]

        tmpoutnames = []
        for _ in range(len(dialects)):
            tmpfd, tmpoutname = tempfile.mkstemp(prefix="ccsv_", suffix=".csv")
            os.close(tmpfd)
            tmpoutnames.append(tmpoutname)

        args = []
        for tmpoutname in tmpoutnames:
            args.append("-o")
            args.append(tmpoutname)
        args += tmpfnames

        application = build_application()
        tester = Tester(application)
        tester.test_command("standardize", args)

        self.assertEqual(tester.get_return_code(), 0)

        exp = "\r\n".join([",".join(map(str, row)) for row in table]) + "\r\n"

        try:
            for tmpoutname in tmpoutnames:
                with open(tmpoutname, "r", newline="") as fp:
                    contents = fp.read()
                self.assertEqual(contents, exp)
        finally:
            any(map(os.unlink, tmpfnames))
            any(map(os.unlink, tmpoutnames))

    def test_standardize_multi_errors(self) -> None:
        table: TableType = [
            ["A", "B", "C"],
            [1, 2, 3],
            [4, 5, 6],
        ]
        dialects = ["excel", "unix", "excel-tab"]
        tmpfnames = [self._build_file(table, D, newline="") for D in dialects]

        tmpoutnames = []
        for _ in range(1):
            tmpfd, tmpoutname = tempfile.mkstemp(prefix="ccsv_", suffix=".csv")
            os.close(tmpfd)
            tmpoutnames.append(tmpoutname)

        args = []
        for tmpoutname in tmpoutnames:
            args.append("-o")
            args.append(tmpoutname)
        args += tmpfnames

        application = build_application()
        tester = Tester(application)
        tester.test_command("standardize", args)

        self.assertEqual(tester.get_return_code(), 1)

        self.assertEqual(
            tester.get_stderr(),
            "Number of output files should match the number of input files.\n",
        )

        any(map(os.unlink, tmpfnames))
        any(map(os.unlink, tmpoutnames))

    def test_standardize_multi_encoding(self) -> None:
        table: TableType = [
            ["Å", "B", "C"],
            [1, 2, 3],
            [4, 5, 6],
        ]
        dialects = ["excel", "unix", "excel-tab"]
        encoding = "ISO-8859-1"
        tmpfnames = [
            self._build_file(table, D, newline="", encoding=encoding)
            for D in dialects
        ]

        tmpoutnames = []
        for _ in range(len(dialects)):
            tmpfd, tmpoutname = tempfile.mkstemp(prefix="ccsv_", suffix=".csv")
            os.close(tmpfd)
            tmpoutnames.append(tmpoutname)

        args = ["-e", encoding]
        for tmpoutname in tmpoutnames:
            args.append("-o")
            args.append(tmpoutname)
        args += tmpfnames

        application = build_application()
        tester = Tester(application)
        tester.test_command("standardize", args)

        self.assertEqual(tester.get_return_code(), 0)

        exp = "\r\n".join([",".join(map(str, row)) for row in table]) + "\r\n"

        try:
            for tmpoutname in tmpoutnames:
                with open(
                    tmpoutname, "r", newline="", encoding=encoding
                ) as fp:
                    contents = fp.read()
                self.assertEqual(contents, exp)
        finally:
            any(map(os.unlink, tmpfnames))
            any(map(os.unlink, tmpoutnames))

    def test_standardize_in_place_multi(self) -> None:
        table: TableType = [
            ["Å", "B", "C"],
            [1, 2, 3],
            [4, 5, 6],
        ]
        dialects = ["excel", "unix", "excel-tab"]
        encoding = "ISO-8859-1"
        tmpfnames = [
            self._build_file(table, D, newline="", encoding=encoding)
            for D in dialects
        ]

        application = build_application()
        tester = Tester(application)
        tester.test_command("standardize", ["-i", "-e", encoding, *tmpfnames])

        self.assertEqual(tester.get_return_code(), 2)

        exp = "\r\n".join([",".join(map(str, row)) for row in table]) + "\r\n"

        try:
            for tmpfname in tmpfnames:
                with open(tmpfname, "r", newline="", encoding=encoding) as fp:
                    contents = fp.read()
                self.assertEqual(contents, exp)
        finally:
            any(map(os.unlink, tmpfnames))

    def test_standardize_in_place_multi_noop(self) -> None:
        table: TableType = [
            ["Å", "B", "C"],
            [1, 2, 3],
            [4, 5, 6],
        ]
        dialects = ["excel", "excel", "excel"]
        tmpfnames = [self._build_file(table, D, newline="") for D in dialects]

        application = build_application()
        tester = Tester(application)
        tester.test_command("standardize", ["-i", *tmpfnames])

        self.assertEqual(tester.get_return_code(), 0)

        exp = "\r\n".join([",".join(map(str, row)) for row in table]) + "\r\n"
        try:
            for tmpfname in tmpfnames:
                with open(tmpfname, "r", newline="") as fp:
                    contents = fp.read()
                self.assertEqual(contents, exp)
        finally:
            any(map(os.unlink, tmpfnames))

    def test_standardize_target_encoding(self) -> None:
        table: TableType = [["Å", "B", "C"], ["é", "ü", "中"], [4, 5, 6]]
        dialect = SimpleDialect(delimiter=";", quotechar="", escapechar="")
        encoding = "utf-8"
        tmpfname = self._build_file(table, dialect, encoding=encoding)

        tmpfd, tmpoutname = tempfile.mkstemp(prefix="ccsv_", suffix=".csv")
        os.close(tmpfd)

        application = build_application()
        tester = Tester(application)
        tester.test_command(
            "standardize", ["-o", tmpoutname, "-E", "utf-8", tmpfname]
        )

        # Excel format (i.e. RFC4180) *requires* CRLF
        crlf = "\r\n"
        exp = crlf.join(["Å,B,C", "é,ü,中", "4,5,6", ""])
        with open(tmpoutname, "r", newline="", encoding="utf-8") as fp:
            output = fp.read()

        try:
            self.assertEqual(exp, output)
        finally:
            os.unlink(tmpfname)
            os.unlink(tmpoutname)

    def test_standardize_target_encoding2(self) -> None:
        table: TableType = [["A", "B", "C"], ["é", "è", "à"], [4, 5, 6]]
        dialect = SimpleDialect(delimiter=";", quotechar="", escapechar="")
        encoding = "latin-1"
        tmpfname = self._build_file(table, dialect, encoding=encoding)
        self.assertEqual(
            "ISO-8859-1", get_encoding(tmpfname, try_cchardet=False)
        )
        tmpfd, tmpoutname = tempfile.mkstemp(prefix="ccsv_", suffix=".csv")
        os.close(tmpfd)

        application = build_application()
        tester = Tester(application)
        tester.test_command(
            "standardize",
            ["-o", tmpoutname, "-e", "latin-1", "-E", "utf-8", tmpfname],
        )

        # Excel format (i.e. RFC4180) *requires* CRLF
        crlf = "\r\n"
        exp = crlf.join(["A,B,C", "é,è,à", "4,5,6", ""])

        self.assertEqual("utf-8", get_encoding(tmpoutname, try_cchardet=False))
        with open(tmpoutname, "r", newline="", encoding="utf-8") as fp:
            output = fp.read()

        try:
            self.assertEqual(exp, output)

        finally:
            os.unlink(tmpfname)
            os.unlink(tmpoutname)

    def test_standardize_target_encoding_raise_UnicodeEncodeError(
        self,
    ) -> None:
        table: TableType = [["Å", "B", "C"], ["é", "ü", "中"], [4, 5, 6]]
        dialect = SimpleDialect(delimiter=";", quotechar="", escapechar="")
        encoding = "utf-8"
        tmpfname = self._build_file(table, dialect, encoding=encoding)

        tmpfd, tmpoutname = tempfile.mkstemp(prefix="ccsv_", suffix=".csv")
        os.close(tmpfd)

        application = build_application()
        tester = Tester(application)
        try:
            with self.assertRaises(UnicodeEncodeError):
                tester.test_command(
                    "standardize",
                    ["-o", tmpoutname, "-E", "latin-1", tmpfname],
                )
        finally:
            os.unlink(tmpfname)
            os.unlink(tmpoutname)
