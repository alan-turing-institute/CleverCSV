# -*- coding: utf-8 -*-

"""
Drop-in replacement for the Python csv reader class. This is a wrapper for the 
Parser class, defined in :mod:`parser`.

Author: Gertjan van den Burg

"""

import csv

from .dialect import SimpleDialect
from .parser import Parser


class reader(object):
    def __init__(self, csvfile, dialect="excel", **fmtparams):
        self.csvfile = csvfile
        self.original_dialect = dialect
        self.dialect = self._make_simple_dialect(dialect, **fmtparams)
        self.line_num = 0
        self.parser_gen = None

    def _make_simple_dialect(self, dialect, **fmtparams):
        if isinstance(dialect, str):
            sd = SimpleDialect.from_csv_dialect(csv.get_dialect(dialect))
        elif isinstance(dialect, csv.Dialect):
            sd = SimpleDialect.from_csv_dialect(dialect)
        elif isinstance(dialect, SimpleDialect):
            sd = dialect
        for key, value in fmtparams.items():
            if key in ["delimiter", "quotechar", "escapechar", "strict"]:
                setattr(sd, key, value)
        sd.validate()
        return sd

    def __iter__(self):
        self.parser = Parser(self.dialect)
        self.parser_gen = self.parser.parse(self.csvfile)
        return self

    def __next__(self):
        if self.parser_gen is None:
            self.__iter__()
        row = next(self.parser_gen)
        self.line_num += 1
        return row

    def next(self):
        # for python 2
        return self.__next__()
