# -*- coding: utf-8 -*-

"""
Unit tests for the DictReader and DictWriter classes

Most of these are the same as in CPython, but we also test the cases where 
CleverCSV's behavior differs.

"""

import io
import tempfile
import unittest

import clevercsv


class DictTestCase(unittest.TestCase):

    ############################
    # Start tests from CPython #

    def test_writeheader_return_value(self):
        with tempfile.TemporaryFile("w+", newline="") as fp:
            writer = clevercsv.DictWriter(fp, fieldnames=["f1", "f2", "f3"])
            writeheader_return_value = writer.writeheader()
            self.assertEqual(writeheader_return_value, 10)

    def test_write_simple_dict(self):
        with tempfile.TemporaryFile("w+", newline="") as fp:
            writer = clevercsv.DictWriter(fp, fieldnames=["f1", "f2", "f3"])
            writer.writeheader()
            fp.seek(0)
            self.assertEqual(fp.readline(), "f1,f2,f3\r\n")
            writer.writerow({"f1": 10, "f3": "abc"})
            fp.seek(0)
            fp.readline()  # header
            self.assertEqual(fp.read(), "10,,abc\r\n")

    def test_write_multiple_dict_rows(self):
        fp = io.StringIO()
        writer = clevercsv.DictWriter(fp, fieldnames=["f1", "f2", "f3"])
        writer.writeheader()
        self.assertEqual(fp.getvalue(), "f1,f2,f3\r\n")
        writer.writerows(
            [
                {"f1": 1, "f2": "abc", "f3": "f"},
                {"f1": 2, "f2": 5, "f3": "xyz"},
            ]
        )
        self.assertEqual(fp.getvalue(), "f1,f2,f3\r\n1,abc,f\r\n2,5,xyz\r\n")

    def test_write_no_fields(self):
        fp = io.StringIO()
        self.assertRaises(TypeError, clevercsv.DictWriter, fp)

    def test_write_fields_not_in_fieldnames(self):
        with tempfile.TemporaryFile("w+", newline="") as fp:
            writer = clevercsv.DictWriter(fp, fieldnames=["f1", "f2", "f3"])
            # Of special note is the non-string key (CPython issue 19449)
            with self.assertRaises(ValueError) as cx:
                writer.writerow({"f4": 10, "f2": "spam", 1: "abc"})
            exception = str(cx.exception)
            self.assertIn("fieldnames", exception)
            self.assertIn("'f4'", exception)
            self.assertNotIn("'f2'", exception)
            self.assertIn("1", exception)

    def test_typo_in_extrasaction_raises_error(self):
        fp = io.StringIO()
        self.assertRaises(
            ValueError,
            clevercsv.DictWriter,
            fp,
            ["f1", "f2"],
            extrasaction="raised",
        )

    def test_write_field_not_in_field_names_raise(self):
        fp = io.StringIO()
        writer = clevercsv.DictWriter(fp, ["f1", "f2"], extrasaction="raise")
        dictrow = {"f0": 0, "f1": 1, "f2": 2, "f3": 3}
        self.assertRaises(
            ValueError, clevercsv.DictWriter.writerow, writer, dictrow
        )

    def test_write_field_not_in_field_names_ignore(self):
        fp = io.StringIO()
        writer = clevercsv.DictWriter(fp, ["f1", "f2"], extrasaction="ignore")
        dictrow = {"f0": 0, "f1": 1, "f2": 2, "f3": 3}
        clevercsv.DictWriter.writerow(writer, dictrow)
        self.assertEqual(fp.getvalue(), "1,2\r\n")

    def test_read_dict_fields(self):
        with tempfile.TemporaryFile("w+") as fp:
            fp.write("1,2,abc\r\n")
            fp.seek(0)
            reader = clevercsv.DictReader(fp, fieldnames=["f1", "f2", "f3"])
            self.assertEqual(next(reader), {"f1": "1", "f2": "2", "f3": "abc"})

    def test_read_dict_no_fieldnames(self):
        with tempfile.TemporaryFile("w+") as fp:
            fp.write("f1,f2,f3\r\n1,2,abc\r\n")
            fp.seek(0)
            reader = clevercsv.DictReader(fp)
            self.assertEqual(next(reader), {"f1": "1", "f2": "2", "f3": "abc"})
            self.assertEqual(reader.fieldnames, ["f1", "f2", "f3"])

    # Two test cases to make sure existing ways of implicitly setting
    # fieldnames continue to work.  Both arise from discussion in issue3436.
    def test_read_dict_fieldnames_from_file(self):
        with tempfile.TemporaryFile("w+") as fp:
            fp.write("f1,f2,f3\r\n1,2,abc\r\n")
            fp.seek(0)
            reader = clevercsv.DictReader(
                fp, fieldnames=next(clevercsv.reader(fp))
            )
            self.assertEqual(reader.fieldnames, ["f1", "f2", "f3"])
            self.assertEqual(next(reader), {"f1": "1", "f2": "2", "f3": "abc"})

    def test_read_dict_fieldnames_chain(self):
        import itertools

        with tempfile.TemporaryFile("w+") as fp:
            fp.write("f1,f2,f3\r\n1,2,abc\r\n")
            fp.seek(0)
            reader = clevercsv.DictReader(fp)
            first = next(reader)
            for row in itertools.chain([first], reader):
                self.assertEqual(reader.fieldnames, ["f1", "f2", "f3"])
                self.assertEqual(row, {"f1": "1", "f2": "2", "f3": "abc"})

    def test_read_long(self):
        with tempfile.TemporaryFile("w+") as fp:
            fp.write("1,2,abc,4,5,6\r\n")
            fp.seek(0)
            reader = clevercsv.DictReader(fp, fieldnames=["f1", "f2"])
            self.assertEqual(
                next(reader),
                {"f1": "1", "f2": "2", None: ["abc", "4", "5", "6"]},
            )

    def test_read_long_with_rest(self):
        with tempfile.TemporaryFile("w+") as fp:
            fp.write("1,2,abc,4,5,6\r\n")
            fp.seek(0)
            reader = clevercsv.DictReader(
                fp, fieldnames=["f1", "f2"], restkey="_rest"
            )
            self.assertEqual(
                next(reader),
                {"f1": "1", "f2": "2", "_rest": ["abc", "4", "5", "6"]},
            )

    def test_read_long_with_rest_no_fieldnames(self):
        with tempfile.TemporaryFile("w+") as fp:
            fp.write("f1,f2\r\n1,2,abc,4,5,6\r\n")
            fp.seek(0)
            reader = clevercsv.DictReader(fp, restkey="_rest")
            self.assertEqual(reader.fieldnames, ["f1", "f2"])
            self.assertEqual(
                next(reader),
                {"f1": "1", "f2": "2", "_rest": ["abc", "4", "5", "6"]},
            )

    def test_read_short(self):
        with tempfile.TemporaryFile("w+") as fp:
            fp.write("1,2,abc,4,5,6\r\n1,2,abc\r\n")
            fp.seek(0)
            reader = clevercsv.DictReader(
                fp, fieldnames="1 2 3 4 5 6".split(), restval="DEFAULT"
            )
            self.assertEqual(
                next(reader),
                {"1": "1", "2": "2", "3": "abc", "4": "4", "5": "5", "6": "6"},
            )
            self.assertEqual(
                next(reader),
                {
                    "1": "1",
                    "2": "2",
                    "3": "abc",
                    "4": "DEFAULT",
                    "5": "DEFAULT",
                    "6": "DEFAULT",
                },
            )

    def test_read_multi(self):
        sample = [
            "2147483648,43.0e12,17,abc,def\r\n",
            "147483648,43.0e2,17,abc,def\r\n",
            "47483648,43.0,170,abc,def\r\n",
        ]

        reader = clevercsv.DictReader(
            sample, fieldnames="i1 float i2 s1 s2".split()
        )
        self.assertEqual(
            next(reader),
            {
                "i1": "2147483648",
                "float": "43.0e12",
                "i2": "17",
                "s1": "abc",
                "s2": "def",
            },
        )

    def test_read_with_blanks(self):
        reader = clevercsv.DictReader(
            ["1,2,abc,4,5,6\r\n", "\r\n", "1,2,abc,4,5,6\r\n"],
            fieldnames="1 2 3 4 5 6".split(),
        )
        self.assertEqual(
            next(reader),
            {"1": "1", "2": "2", "3": "abc", "4": "4", "5": "5", "6": "6"},
        )
        self.assertEqual(
            next(reader),
            {"1": "1", "2": "2", "3": "abc", "4": "4", "5": "5", "6": "6"},
        )

    def test_read_semi_sep(self):
        reader = clevercsv.DictReader(
            ["1;2;abc;4;5;6\r\n"],
            fieldnames="1 2 3 4 5 6".split(),
            delimiter=";",
        )
        self.assertEqual(
            next(reader),
            {"1": "1", "2": "2", "3": "abc", "4": "4", "5": "5", "6": "6"},
        )

    # End tests from CPython #
    ##########################

    ###################################
    # Start tests added for CleverCSV #

    def test_read_duplicate_fieldnames(self):
        reader = clevercsv.DictReader(["f1,f2,f1\r\n", "a", "b", "c"])
        with self.assertWarns(UserWarning):
            reader.fieldnames

    # End tests added for CleverCSV #
    #################################


if __name__ == "__main__":
    unittest.main()
