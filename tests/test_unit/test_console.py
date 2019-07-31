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
    def _build_file(self, table, dialect, encoding=None):
        tmpfd, tmpfname = tempfile.mkstemp(suffix=".csv")
        tmpid = os.fdopen(tmpfd, "w", encoding=encoding)
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

df = clevercsv.csv2df("{tmpfname}", delimiter=";", quotechar="", escapechar="")

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

    def test_standardize_1(self):
        table = [["A", "B", "C"], [1, 2, 3], [4, 5, 6]]
        dialect = SimpleDialect(delimiter=";", quotechar="", escapechar="")
        tmpfname = self._build_file(table, dialect)

        application = build_application()
        command = application.find("standardize")
        tester = CommandTester(command)
        tester.execute(tmpfname)

        exp = "A,B,C\n1,2,3\n4,5,6"
        try:
            output = tester.io.fetch_output().strip()
            self.assertEqual(exp, output)
        finally:
            os.unlink(tmpfname)

    def test_standardize_2(self):
        table = [["A", "B", "C"], [1, 2, 3], [4, 5, 6]]
        dialect = SimpleDialect(delimiter=";", quotechar="", escapechar="")
        tmpfname = self._build_file(table, dialect)

        tmpfd, tmpoutname = tempfile.mkstemp(suffix=".csv")
        os.close(tmpfd)

        application = build_application()
        command = application.find("standardize")
        tester = CommandTester(command)
        tester.execute(f"-o {tmpoutname} {tmpfname}")

        exp = "A,B,C\n1,2,3\n4,5,6\n"
        with open(tmpoutname, "r") as fp:
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

        tmpfd, tmpoutname = tempfile.mkstemp(suffix=".csv")
        os.close(tmpfd)

        application = build_application()
        command = application.find("standardize")
        tester = CommandTester(command)
        tester.execute(f"-t {tmpfname}")

        exp = "A,1,4\nB,2,5\nC,3,6"

        try:
            output = tester.io.fetch_output().strip()
            self.assertEqual(exp, output)
        finally:
            os.unlink(tmpfname)
