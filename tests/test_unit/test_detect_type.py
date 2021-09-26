# -*- coding: utf-8 -*-

"""
Unit tests for the type detection.

Author: Gertjan van den Burg

"""

import unittest

from clevercsv.detect_type import TypeDetector
from clevercsv.detect_type import type_score
from clevercsv.dialect import SimpleDialect


class TypeDetectorTestCase(unittest.TestCase):
    def setUp(self):
        self.td = TypeDetector()

    # NUMBERS

    def test_number(self):
        yes_number = [
            "1",
            "2",
            "34",
            "56",
            "123",
            "789",
            "132.",
            "0.123",
            "0.10800212",
            "0.1231e-087",
            "10.789e09",
            "123.256e+08",
            "0.1231E-087",
            "10.789E09",
            "123.256E+08",
            "123,456,798.00",
            "23,456.798",
            "1,234.56",
            "1,123.",
            "1e5",
            "1.23e5",
            "-1",
            "-2",
            "-34",
            "-56",
            "-123",
            "-789",
            "-0.123",
            "-0.10800212",
            "-0.1231e-087",
            "-10.789e09",
            "-123.256e+08",
            "-0.1231E-087",
            "-10.789E09",
            "-123.256E+08",
            "-123,456,798.00",
            "-23,456.798",
            "-1,234.56",
            "+1",
            "+2",
            "+34",
            "+56",
            "+123",
            "+789",
            "+0.123",
            "+0.10800212",
            "+0.1231e-087",
            "+10.789e09",
            "+123.256e+08",
            "+0.1231E-087",
            "+10.789E09",
            "+123.256E+08",
            "+123,456,798.00",
            "+23,456.798",
            "+1,234.56",
            ".707",
            "-.707",
            "50,000.123",
            "1.000,123",
            "37.e88",
            "1.",
        ]
        for num in yes_number:
            with self.subTest(num=num):
                self.assertTrue(self.td.is_number(num))
        no_number = [
            "0000.213654",
            "123.465.798",
            "0.5e0.5",
            "1,23.45",
            "12,34.56",
            "+00003",
            "0,132.6",
            "1,",
            "",
            "E14000537",
            "0e",
            ".",
            ",",
            "+E3",
            "1,",
        ]
        for num in no_number:
            with self.subTest(num=num):
                self.assertFalse(self.td.is_number(num))

    # DATES

    def test_date(self):
        yes_date = [
            "031219",
            "03122019",
            "03-12-19",
            "03-12-2019",
            "03-5-19",
            "03-5-2019",
            "120319",
            "12032019",
            "12-03-19",
            "02-03-2019",
            "02-3-19",
            "02-3-2019",
            "19-12-3",
            "19-12-03",
            "19-2-3",
            "19-2-03",
            "8-21-19",
            "8-21-2019",
            "8-9-19",
            "8-9-2019",
            "7-12-19",
            "7-12-2019",
            "3-9-19",
            "3-9-2019",
            "191203",
            "20191121",
            "2019-12-3",
            "2019-12-21",
            "2019-3-9",
            "2019-3-21",
            "2019年11月21日",
            "2019年11月1日",
            "2019年3月21日",
            "2019年3月1日",
            "19年03月11日",
            "19年03月1日",
            "19年3月31日",
            "19年3月1日",
            "2019년11월21일",
            "2019년11월1일",
            "2019년3월21일",
            "2019년3월1일",
            "19년03월11일",
            "19년03월1일",
            "19년3월31일",
            "19년3월1일",
        ]
        for date in yes_date:
            with self.subTest(date=date):
                self.assertTrue(self.td.is_date(date))
        no_date = [
            "2018|01|02",
            "30/07-88",
            "12.01-99",
            "5.024.2896",
            "2512-012.1",
            "12 01/2542",
        ]
        for date in no_date:
            with self.subTest(date=date):
                self.assertFalse(self.td.is_date(date))

    # DATETIME

    def test_datetime(self):
        yes_dt = ["2019-01-12T04:01:23Z", "2021-09-26T12:13:31+01:00"]
        for dt in yes_dt:
            with self.subTest(dt=dt):
                self.assertTrue(self.td.is_datetime(dt))
        no_date = []
        for date in no_date:
            with self.subTest(date=date):
                self.assertFalse(self.td.is_datetime(dt))

    # URLs

    def test_url(self):
        # Some cases copied from https://mathiasbynens.be/demo/url-regex
        yes_url = [
            "Cocoal.icio.us",
            "Websquash.com",
            "bbc.co.uk",
            "ebay.com",
            "en.wikipedia.com",
            "ftp://foo.bar/baz",
            "http://127.0.0.1",
            "http://127.0.0.1/uoshostel/web/app_dev.php/assets/img/size2.jpg",
            "http://1337.net",
            "http://142.42.1.1/",
            "http://142.42.1.1:8080/",
            "http://223.255.255.254",
            "http://a.b-c.de",
            "http://code.google.com/events/#&product=browser",
            "http://en.wikipedia.com",
            "http://experiment.local/frameworks/symphony2/web/app_dev.php/admin/categories",
            "http://foo.bar/?q=Test%20URL-encoded%20stuff",
            "http://foo.com/(something)?after=parens",
            "http://foo.com/blah_(wikipedia)#cite-1",
            "http://foo.com/blah_(wikipedia)_blah#cite-1",
            "http://foo.com/blah_blah",
            "http://foo.com/blah_blah/",
            "http://foo.com/blah_blah_(wikipedia)",
            "http://foo.com/blah_blah_(wikipedia)_(again)",
            "http://fridley-tigers.com",
            "http://gertjan.dev",
            "http://hi.fridley-tigers.com",
            "http://j.mp",
            "http://localhost/1234.html",
            "http://localhost/Symfony/web/app_dev.php/index",
            "http://localhost/pidev/WebSmartravel/web/app_dev.php/travel_admin/1/js/bootstrap.js",
            "http://localhost/webSmartravel/web/app_dev.php/admin",
            "http://mainhostel.localdev.com/app_dev.php/location",
            "http://simplegreensmoothies.com/Recipes/kiwi-strawberry-twist",
            "http://t.co/VSD0L81Yrt",
            "http://t.co/VSD0L81Yrt.html",
            "http://www.bbc.co.uk",
            "http://www.beloithistoricalsociety.com/hanchett.htm",
            "http://www.co-operativefood.co.uk/find-us/?q=UK&lat=52.451935&long=-1.887871&filters=Food&options=",
            "http://www.deutsche-wein-strasse.de/Panorama/Flemlingen/flemlingen.htm",
            "http://www.example.com/wpstyle/?p=364",
            "http://www.google.com/url?q=http%3A%2F%2Fbit.ly%2F1sneR2w&sa=D&sntz=1&usg=AFQjCNGs2NJSTFm8Dzx-755C0K0_KDuiew",
            "http://www.iceland.co.uk/",
            "http://www.iceland.co.uk/store-finder/",
            "http://www.iceland.co.uk/store-finder/?StoreFinderSearch=S45%209JE",
            "http://www.marksandspencer.com/MSStoreDetailsView?SAPStoreId=2804",
            "http://www.sainsburys.co.uk/sol/storelocator/storelocator_detail_view.jsp?storeId=4526&bmForm=store_details",
            "http://www.stackoverflow.com/",
            "https://en.wikipedia.com",
            "https://gertjan.dev",
            "https://google.com",
            "https://localhost",
            "https://www.example.com/foo/?bar=baz&inga=42&quux",
            "test.example.com/~name",
            "www.google.com",
            "www.google.com/",
            "www.menominee-nsn.gov/",
            "http://arxiv.org/abs/arXiv:1908.03213",
            "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3474301/",
            "https://dl.acm.org/citation.cfm?id=3025626",
            "https://openreview.net/forum?id=S1x4ghC9tQ",
            "https://link.springer.com/article/10.1007/s10618-019-00631-5",
            "http://proceedings.mlr.press/v48/zhangf16.html",
            "https://papers.nips.cc/paper/7796-middle-out-decoding",
            "http://citeseerx.ist.psu.edu/viewdoc/summary?doi=10.1.1.89.6548",
            "http://localhost:81/test/web/app_dev.php/fr/intranet/admin/client/2",
        ]
        for url in yes_url:
            with self.subTest(url=url):
                self.assertTrue(self.td.is_url(url))

        no_url = [
            "//",
            "///",
            "///a",
            "//a",
            ":// should fail",
            "a@b.com",
            "ftps://foo.bar/",
            "h://test",
            "http:// shouldfail.com",
            "http://",
            "http://#",
            "http://##",
            "http://##/",
            "http://-a.b.co",
            "http://-error-.invalid/",
            "http://.",
            "http://..",
            "http://../",
            "http://.www.foo.bar./",
            "http://.www.foo.bar/",
            "http:///a",
            "http://1.1.1.1.1",
            "http://123.123.123",
            "http://3628126748",
            "http://?",
            "http://??",
            "http://??/",
            "http://foo.bar/foo(bar)baz quux",
            "http://foo.bar?q=Spaces should be encoded",
            "http://www.foo.bar./",
            "rdar://1234",
        ]
        for url in no_url:
            with self.subTest(url=url):
                self.assertFalse(self.td.is_url(url))

    # Unicode_alphanum

    def test_unicode_alphanum(self):
        # These tests are by no means inclusive and ought to be extended in the
        # future.

        yes_alphanum = ["this is a cell", "1231 pounds"]
        for unicode_alphanum in yes_alphanum:
            with self.subTest(unicode_alphanum=unicode_alphanum):
                self.assertTrue(self.td.is_unicode_alphanum(unicode_alphanum))
                self.assertTrue(
                    self.td.is_unicode_alphanum(
                        unicode_alphanum, is_quoted=True
                    )
                )

        no_alphanum = ["https://www.gertjan.dev"]
        for unicode_alpanum in no_alphanum:
            with self.subTest(unicode_alpanum=unicode_alpanum):
                self.assertFalse(self.td.is_unicode_alphanum(unicode_alpanum))
                self.assertFalse(
                    self.td.is_unicode_alphanum(
                        unicode_alpanum, is_quoted=True
                    )
                )

        only_quoted = ["this string, with a comma"]
        for unicode_alpanum in only_quoted:
            with self.subTest(unicode_alpanum=unicode_alpanum):
                self.assertFalse(
                    self.td.is_unicode_alphanum(
                        unicode_alpanum,
                    )
                )
                self.assertTrue(
                    self.td.is_unicode_alphanum(
                        unicode_alpanum, is_quoted=True
                    )
                )

    def test_bytearray(self):
        yes_bytearray = [
            "bytearray(b'')",
            "bytearray(b'abc,*&@\"')",
            "bytearray(b'bytearray(b'')')",
        ]
        no_bytearray = [
            "bytearray(b'abc",
            "bytearray(b'abc'",
            "bytearray('abc')",
            "abc,bytearray(b'def')",
        ]

        for case in yes_bytearray:
            with self.subTest(case=case):
                self.assertTrue(self.td.is_bytearray(case))

        for case in no_bytearray:
            with self.subTest(case=case):
                self.assertFalse(self.td.is_bytearray(case))

    # Unix path

    def test_unix_path(self):
        yes_path = [
            "/Users/person/abc/def-ghi/blabla.csv.test",
            "/home/username/share/a/_b/c_d/e.py",
            "/home/username/share",
            "/home/username",
            "/home/username/",
            "~/share/",
            "./share",
        ]
        for path in yes_path:
            with self.subTest(path=path):
                self.assertTrue(self.td.is_unix_path(path))
        no_path = ["", "~share", ".share"]
        for path in no_path:
            with self.subTest(path=path):
                self.assertFalse(self.td.is_unix_path(path))

    """
    Type Score tests
    """

    def test_type_score_1(self):
        # theta_1 from paper
        cells = [
            ["7", "5; Mon", " Jan 12;6", "40"],
            ["100; Fri", " Mar 21;8", "23"],
            ["8", "2; Thu", " Sep 17; 2", "71"],
            ["538", "0;;7", "26"],
            ['"NA"; Wed', " Oct 4;6", "93"],
        ]
        data = "\n".join([",".join(x) for x in cells])
        dialect = SimpleDialect(delimiter=",", quotechar="", escapechar="")
        out = type_score(data, dialect)
        exp = 8 / 17
        self.assertAlmostEqual(exp, out)

    def test_type_score_2(self):
        # theta_2 from paper
        cells = [
            ["7,5", " Mon, Jan 12", "6,40"],
            ["100", " Fri, Mar 21", "8,23"],
            ["8,2", " Thu, Sep 17", "2,71"],
            ["538,0", "", "7,26"],
            ['"N/A"', " Wed, Oct 4", "6,93"],
        ]
        data = "\r\n".join([";".join(x) for x in cells])
        dialect = SimpleDialect(delimiter=";", quotechar="", escapechar="")
        out = type_score(data, dialect)
        exp = 10 / 15
        self.assertAlmostEqual(exp, out)

    def test_type_score_3(self):
        # theta_3 from paper
        cells = [
            ["7,5", " Mon, Jan 12", "6,40"],
            ["100", " Fri, Mar 21", "8,23"],
            ["8,2", " Thu, Sep 17", "2,71"],
            ["538,0", "", "7,26"],
            ["N/A", " Wed, Oct 4", "6,93"],
        ]
        data = "\r".join([";".join(x) for x in cells])
        dialect = SimpleDialect(delimiter=";", quotechar='"', escapechar="")
        out = type_score(data, dialect)
        exp = 11 / 15
        self.assertAlmostEqual(exp, out)


if __name__ == "__main__":
    unittest.main()
