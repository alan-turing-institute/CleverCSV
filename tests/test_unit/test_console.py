# -*- coding: utf-8 -*-

"""
Unit tests for the console application.

Author: Gertjan van den Burg
"""

import os
import tempfile
import unittest

from cleo.testers import CommandTester

from clevercsv import __version__
from clevercsv.console import build_application
from clevercsv.dialect import SimpleDialect
from clevercsv.write import writer


class ConsoleTestCase(unittest.TestCase):
    def _build_file(self, table, dialect, encoding=None, newline=None):
        tmpfd, tmpfname = tempfile.mkstemp(
            prefix="ccsv_",
            suffix=".csv",
        )
        tmpid = os.fdopen(tmpfd, "w", newline=newline, encoding=encoding)
        w = writer(tmpid, dialect=dialect)
        w.writerows(table)
        tmpid.close()
        return tmpfname

    def _detect_test_wrap(self, table, dialect):
        tmpfname = self._build_file(table, dialect)
        exp = "Detected: " + str(dialect)

        application = build_application()
        command = application.find("detect")
        tester = CommandTester(command)
        tester.execute(tmpfname)

        try:
            output = tester.io.fetch_output().strip()
            self.assertEqual(exp, output)
        finally:
            os.unlink(tmpfname)

    def test_detect_base(self):
        table = [["A", "B", "C"], [1, 2, 3], [4, 5, 6]]
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

    def test_detect_opts_1(self):
        table = [["A", "B", "C"], [1, 2, 3], [4, 5, 6]]
        dialect = SimpleDialect(delimiter=";", quotechar="", escapechar="")
        encoding = "windows-1252"
        tmpfname = self._build_file(table, dialect, encoding=encoding)

        application = build_application()
        command = application.find("detect")
        tester = CommandTester(command)
        tester.execute(f"--encoding '{encoding}' {tmpfname}")

        exp = "Detected: " + str(dialect)

        try:
            output = tester.io.fetch_output().strip()
            self.assertEqual(exp, output)
        finally:
            os.unlink(tmpfname)

    def test_detect_opts_2(self):
        table = [["A", "B", "C"], [1, 2, 3], [4, 5, 6]]
        dialect = SimpleDialect(delimiter=";", quotechar="", escapechar="")
        tmpfname = self._build_file(table, dialect)

        application = build_application()
        command = application.find("detect")
        tester = CommandTester(command)
        tester.execute(f"--num-chars 5 {tmpfname}")

        exp = "Detected: " + str(dialect)

        try:
            output = tester.io.fetch_output().strip()
            self.assertEqual(exp, output)
        finally:
            os.unlink(tmpfname)

    def test_detect_opts_3(self):
        table = [["A", "B", "C"], [1, 2, 3], [4, 5, 6]]
        dialect = SimpleDialect(delimiter=";", quotechar="", escapechar="")
        tmpfname = self._build_file(table, dialect)

        application = build_application()
        command = application.find("detect")
        tester = CommandTester(command)
        tester.execute(f"--plain {tmpfname}")

        exp = """\
delimiter = ;
quotechar =
escapechar ="""
        try:
            output = tester.io.fetch_output().strip()
            self.assertEqual(exp, output)
        finally:
            os.unlink(tmpfname)

    def test_code_1(self):
        table = [["A", "B", "C"], [1, 2, 3], [4, 5, 6]]
        dialect = SimpleDialect(delimiter=";", quotechar="", escapechar="")

        tmpfname = self._build_file(table, dialect)

        application = build_application()
        command = application.find("code")
        tester = CommandTester(command)
        tester.execute(tmpfname)

        exp = f"""\

# Code generated with CleverCSV version {__version__}

import clevercsv

with open("{tmpfname}", "r", newline="", encoding="ascii") as fp:
    reader = clevercsv.reader(fp, delimiter=";", quotechar="", escapechar="")
    rows = list(reader)

"""
        try:
            output = tester.io.fetch_output()
            self.assertEqual(exp, output)
        finally:
            os.unlink(tmpfname)

    def test_code_2(self):
        table = [["A", "B", "C"], [1, 2, 3], [4, 5, 6]]
        dialect = SimpleDialect(delimiter=";", quotechar="", escapechar="")
        tmpfname = self._build_file(table, dialect)

        application = build_application()
        command = application.find("code")
        tester = CommandTester(command)
        tester.execute(f"-p {tmpfname}")

        exp = f"""\

# Code generated with CleverCSV version {__version__}

import clevercsv

df = clevercsv.read_dataframe("{tmpfname}", delimiter=";", quotechar="", escapechar="")

"""
        try:
            output = tester.io.fetch_output()
            self.assertEqual(exp, output)
        finally:
            os.unlink(tmpfname)

    def test_code_3(self):
        table = [["Å", "B", "C"], [1, 2, 3], [4, 5, 6]]
        dialect = SimpleDialect(delimiter=";", quotechar="", escapechar="")
        encoding = "ISO-8859-1"
        tmpfname = self._build_file(table, dialect, encoding=encoding)

        application = build_application()
        command = application.find("code")
        tester = CommandTester(command)
        tester.execute(tmpfname)

        exp = f"""\

# Code generated with CleverCSV version {__version__}

import clevercsv

with open("{tmpfname}", "r", newline="", encoding="{encoding}") as fp:
    reader = clevercsv.reader(fp, delimiter=";", quotechar="", escapechar="")
    rows = list(reader)

"""
        try:
            output = tester.io.fetch_output()
            self.assertEqual(exp, output)
        finally:
            os.unlink(tmpfname)

    def test_code_4(self):
        table = [["Å", "B,D", "C"], [1, 2, 3], [4, 5, 6]]
        dialect = SimpleDialect(delimiter=",", quotechar="", escapechar="\\")
        encoding = "ISO-8859-1"
        tmpfname = self._build_file(table, dialect, encoding=encoding)

        application = build_application()
        command = application.find("code")
        tester = CommandTester(command)
        tester.execute(tmpfname)

        exp = f"""\

# Code generated with CleverCSV version {__version__}

import clevercsv

with open("{tmpfname}", "r", newline="", encoding="{encoding}") as fp:
    reader = clevercsv.reader(fp, delimiter=",", quotechar="", escapechar="\\\\")
    rows = list(reader)

"""
        try:
            output = tester.io.fetch_output()
            self.assertEqual(exp, output)
        finally:
            os.unlink(tmpfname)

    def test_code_5(self):
        table = [["A", "B", "C"], [1, 2, 3], [4, 5, 6]]
        dialect = SimpleDialect(delimiter="\t", quotechar="", escapechar="")

        tmpfname = self._build_file(table, dialect)

        application = build_application()
        command = application.find("code")
        tester = CommandTester(command)
        tester.execute(tmpfname)

        exp = f"""\

# Code generated with CleverCSV version {__version__}

import clevercsv

with open("{tmpfname}", "r", newline="", encoding="ascii") as fp:
    reader = clevercsv.reader(fp, delimiter="\\t", quotechar="", escapechar="")
    rows = list(reader)

"""
        try:
            output = tester.io.fetch_output()
            self.assertEqual(exp, output)
        finally:
            os.unlink(tmpfname)

    def test_standardize_1(self):
        table = [["A", "B", "C"], [1, 2, 3], [4, 5, 6]]
        dialect = SimpleDialect(delimiter=";", quotechar="", escapechar="")
        tmpfname = self._build_file(table, dialect)

        application = build_application()
        command = application.find("standardize")
        tester = CommandTester(command)
        tester.execute(tmpfname)

        # Excel format (i.e. RFC4180) *requires* CRLF
        crlf = "\r\n"
        exp = crlf.join(["A,B,C", "1,2,3", "4,5,6"])
        # add line terminator of last row
        exp += crlf
        try:
            output = tester.io.fetch_output()
            self.assertEqual(exp, output)
        finally:
            os.unlink(tmpfname)

    def test_standardize_2(self):
        table = [["A", "B", "C"], [1, 2, 3], [4, 5, 6]]
        dialect = SimpleDialect(delimiter=";", quotechar="", escapechar="")
        tmpfname = self._build_file(table, dialect)

        tmpfd, tmpoutname = tempfile.mkstemp(prefix="ccsv_", suffix=".csv")
        os.close(tmpfd)

        application = build_application()
        command = application.find("standardize")
        tester = CommandTester(command)
        tester.execute(f"-o {tmpoutname} {tmpfname}")

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

    def test_standardize_3(self):
        table = [["A", "B", "C"], [1, 2, 3], [4, 5, 6]]
        dialect = SimpleDialect(delimiter=";", quotechar="", escapechar="")
        tmpfname = self._build_file(table, dialect)

        application = build_application()
        command = application.find("standardize")
        tester = CommandTester(command)
        tester.execute(f"-t {tmpfname}")

        # Excel format (i.e. RFC4180) *requires* CRLF
        crlf = "\r\n"
        exp = crlf.join(["A,1,4", "B,2,5", "C,3,6"])
        # add line terminator of last row
        exp += crlf

        try:
            output = tester.io.fetch_output()
            self.assertEqual(exp, output)
        finally:
            os.unlink(tmpfname)

    def test_standardize_in_place(self):
        table = [["A", "B", "C"], [1, 2, 3], [4, 5, 6]]
        dialect = SimpleDialect(delimiter=";", quotechar="", escapechar="")
        tmpfname = self._build_file(table, dialect)

        application = build_application()
        command = application.find("standardize")
        tester = CommandTester(command)
        retcode = tester.execute(f"-i {tmpfname}")

        self.assertEqual(retcode, 2)

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

    def test_standardize_in_place_noop(self):
        table = [["A", "B", "C"], [1, 2, 3], [4, 5, 6]]
        dialect = "excel"
        tmpfname = self._build_file(table, dialect, newline="")

        application = build_application()
        command = application.find("standardize")
        tester = CommandTester(command)
        retcode = tester.execute(f"-i {tmpfname}")

        self.assertEqual(retcode, 0)

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

    def test_standardize_multi(self):
        table = [["A", "B", "C"], [1, 2, 3], [4, 5, 6]]
        dialects = ["excel", "unix", "excel-tab"]
        tmpfnames = [self._build_file(table, D, newline="") for D in dialects]

        tmpoutnames = []
        for _ in range(len(dialects)):
            tmpfd, tmpoutname = tempfile.mkstemp(prefix="ccsv_", suffix=".csv")
            os.close(tmpfd)
            tmpoutnames.append(tmpoutname)

        outputs = " ".join([f"-o {tmpoutname}" for tmpoutname in tmpoutnames])

        application = build_application()
        command = application.find("standardize")
        tester = CommandTester(command)
        retcode = tester.execute(f"{outputs} {' '.join(tmpfnames)}")

        self.assertEqual(retcode, 0)

        exp = "\r\n".join([",".join(map(str, row)) for row in table]) + "\r\n"

        try:
            for tmpoutname in tmpoutnames:
                with open(tmpoutname, "r", newline="") as fp:
                    contents = fp.read()
                self.assertEqual(contents, exp)
        finally:
            any(map(os.unlink, tmpfnames))
            any(map(os.unlink, tmpoutnames))

    def test_standardize_multi_errors(self):
        table = [["A", "B", "C"], [1, 2, 3], [4, 5, 6]]
        dialects = ["excel", "unix", "excel-tab"]
        tmpfnames = [self._build_file(table, D, newline="") for D in dialects]

        tmpoutnames = []
        for _ in range(1):
            tmpfd, tmpoutname = tempfile.mkstemp(prefix="ccsv_", suffix=".csv")
            os.close(tmpfd)
            tmpoutnames.append(tmpoutname)

        outputs = " ".join([f"-o {tmpoutname}" for tmpoutname in tmpoutnames])

        application = build_application()
        command = application.find("standardize")
        tester = CommandTester(command)
        retcode = tester.execute(f"{outputs} {' '.join(tmpfnames)}")

        self.assertEqual(retcode, 1)

        stdout = tester.io.fetch_output()
        self.assertEqual(
            stdout,
            "Number of output files should match the number of input files.\n",
        )

        any(map(os.unlink, tmpfnames))
        any(map(os.unlink, tmpoutnames))

    def test_standardize_multi_encoding(self):
        table = [["Å", "B", "C"], [1, 2, 3], [4, 5, 6]]
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

        outputs = " ".join([f"-o {tmpoutname}" for tmpoutname in tmpoutnames])

        application = build_application()
        command = application.find("standardize")
        tester = CommandTester(command)
        retcode = tester.execute(
            f"-e {encoding} {outputs} {' '.join(tmpfnames)}"
        )

        self.assertEqual(retcode, 0)

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

    def test_standardize_in_place_multi(self):
        table = [["Å", "B", "C"], [1, 2, 3], [4, 5, 6]]
        dialects = ["excel", "unix", "excel-tab"]
        encoding = "ISO-8859-1"
        tmpfnames = [
            self._build_file(table, D, newline="", encoding=encoding)
            for D in dialects
        ]

        application = build_application()
        command = application.find("standardize")
        tester = CommandTester(command)
        retcode = tester.execute(f"-i -e {encoding} {' '.join(tmpfnames)}")

        self.assertEqual(retcode, 2)

        exp = "\r\n".join([",".join(map(str, row)) for row in table]) + "\r\n"

        try:
            for tmpfname in tmpfnames:
                with open(tmpfname, "r", newline="", encoding=encoding) as fp:
                    contents = fp.read()
                self.assertEqual(contents, exp)
        finally:
            any(map(os.unlink, tmpfnames))

    def test_standardize_in_place_multi_noop(self):
        table = [["Å", "B", "C"], [1, 2, 3], [4, 5, 6]]
        dialects = ["excel", "excel", "excel"]
        tmpfnames = [self._build_file(table, D, newline="") for D in dialects]

        application = build_application()
        command = application.find("standardize")
        tester = CommandTester(command)
        retcode = tester.execute(f"-i {' '.join(tmpfnames)}")

        self.assertEqual(retcode, 0)

        exp = "\r\n".join([",".join(map(str, row)) for row in table]) + "\r\n"
        try:
            for tmpfname in tmpfnames:
                with open(tmpfname, "r", newline="") as fp:
                    contents = fp.read()
                self.assertEqual(contents, exp)
        finally:
            any(map(os.unlink, tmpfnames))
