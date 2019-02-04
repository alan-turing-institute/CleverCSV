# -*- coding: utf-8 -*-

"""
Integration tests for dialect detection.

This module generates the test cases based on the available annotated CSV 
files. See https://stackoverflow.com/a/20870875/1154005 for the metaclass 
approach that we use here.

Author: G.J.J. van den Burg

"""

import ccsv
import os
import unittest
import warnings
import json
import six

THIS_DIR = os.path.dirname(__file__)
SOURCE_DIR = os.path.join(THIS_DIR, "data")
TEST_FILES = os.path.join(SOURCE_DIR, "files")
TEST_DIALECTS = os.path.join(SOURCE_DIR, "dialects")


def load_test_cases():
    cases = []
    for f in sorted(os.listdir(TEST_FILES)):
        base = os.path.splitext(f)[0]
        dialect_file = os.path.join(TEST_DIALECTS, base + ".json")
        if not os.path.exists(dialect_file):
            continue
        filename = os.path.join(TEST_FILES, f)
        with open(dialect_file, "r") as fid:
            annotation = json.load(fid)
        if not annotation["filename"] == f:
            warnings.warn(
                "filename doesn't match! Input file: %s\nDialect file: %s"
                % (filename, dialect_file)
            )
            continue
        if annotation["status"] == "skip":
            continue
        cases.append((base, filename, annotation["dialect"]))
    return cases


class TestDetectorMeta(type):
    def __new__(mcs, name, bases, dict_):
        def generate_test(filename, true_dialect):
            def test(self):
                det = ccsv.Detector()
                with open(filename, "r", newline="") as fid:
                    dialect = det.detect(fid.read())
                self.assertIsNotNone(det)
                self.assertEqual(dialect.delimiter, true_dialect["delimiter"])
                self.assertEqual(dialect.quotechar, true_dialect["quotechar"])
                self.assertEqual(
                    dialect.escapechar, true_dialect["escapechar"]
                )

            return test

        cases = load_test_cases()
        fmt = "%%0%id" % (len(str(len(cases))))
        for num, (name, filename, dialect) in enumerate(cases):
            test_name = "test_dialect_%s_%s" % (fmt % num, name)
            dict_[test_name] = generate_test(filename, dialect)
        return type.__new__(mcs, name, bases, dict_)


class TestDetector(six.with_metaclass(TestDetectorMeta, unittest.TestCase)):
    pass


if __name__ == "__main__":
    unittest.main()
