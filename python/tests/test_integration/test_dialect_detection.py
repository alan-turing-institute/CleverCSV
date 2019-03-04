# -*- coding: utf-8 -*-

"""
Integration tests for dialect detection.

This module generates the test cases based on the available annotated CSV 
files. See https://stackoverflow.com/q/32939 for more info.

Author: G.J.J. van den Burg

"""

import ccsv
import gzip
import json
import nose
import os
import unittest
import warnings

from parameterized import parameterized
from logresults import LogResults

THIS_DIR = os.path.abspath(os.path.dirname(__file__))
SOURCE_DIR = os.path.join(THIS_DIR, "data")
TEST_FILES = os.path.join(SOURCE_DIR, "files")
TEST_DIALECTS = os.path.join(SOURCE_DIR, "dialects")

LOG_SUCCESS = os.path.join(THIS_DIR, "success.log")
LOG_ERROR = os.path.join(THIS_DIR, "error.log")
LOG_FAILED = os.path.join(THIS_DIR, "failed.log")


def load_test_cases():
    cases = []
    for f in sorted(os.listdir(TEST_FILES)):
        base = f[: -len(".csv.gz")]
        dialect_file = os.path.join(TEST_DIALECTS, base + ".json")
        if not os.path.exists(dialect_file):
            continue
        filename = os.path.join(TEST_FILES, f)
        with open(dialect_file, "r") as fid:
            annotation = json.load(fid)
        if not annotation["filename"] == f[:-len(".gz")]:
            warnings.warn(
                "filename doesn't match! Input file: %s\nDialect file: %s"
                % (filename, dialect_file)
            )
            continue
        if annotation["status"] == "skip":
            continue
        cases.append((base, filename, annotation))
    return cases


class TestDetector(unittest.TestCase):
    @parameterized.expand(load_test_cases)
    def test_dialect(self, name, filename, annotation):
        det = ccsv.Detector()
        if "encoding" in annotation:
            enc = annotation["encoding"]
        else:
            enc = ccsv.utils.get_encoding(filename)
        true_dialect = annotation["dialect"]
        with gzip.open(filename, "rt", newline="", encoding=enc) as fid:
            dialect = det.detect(fid.read())
        self.assertIsNotNone(dialect)
        self.assertEqual(dialect.delimiter, true_dialect["delimiter"])
        self.assertEqual(dialect.quotechar, true_dialect["quotechar"])
        self.assertEqual(dialect.escapechar, true_dialect["escapechar"])


if __name__ == "__main__":
    nose.main(addplugins=[LogResults(LOG_SUCCESS, LOG_ERROR, LOG_FAILED)])
