import unittest

import clevercsv


class CNamingTestCase(unittest.TestCase):
    def test_name_cabstraction_module(self) -> None:
        self.assertEqual(
            clevercsv.cabstraction.__name__, "clevercsv.cabstraction"
        )

    def test_name_cparser_module(self) -> None:
        self.assertEqual(clevercsv.cparser.__name__, "clevercsv.cparser")

    def test_name_cparser_error(self) -> None:
        self.assertEqual(
            clevercsv.cparser.Error.__module__, "clevercsv.cparser"
        )

    def test_name_cparser_parser(self) -> None:
        self.assertEqual(
            clevercsv.cparser.Parser.__module__, "clevercsv.cparser"
        )
