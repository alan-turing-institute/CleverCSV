# -*- coding: utf-8 -*-

"""
Drop-in replacement for the Python csv reader class. This is a wrapper for the 
Parser class, defined in :mod:`cparser`.

Author: Gertjan van den Burg

"""

import csv

from . import field_size_limit
from .cparser import Parser, Error as ParserError
from .dialect import SimpleDialect
from .exceptions import Error


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
        self.parser_gen = Parser(
            self.csvfile,
            delimiter=self.dialect.delimiter,
            quotechar=self.dialect.quotechar,
            escapechar=self.dialect.escapechar,
            field_limit=field_size_limit(),
            strict=self.dialect.strict,
        )
        return self

    def __next__(self):
        if self.parser_gen is None:
            self.__iter__()
        try:
            row = next(self.parser_gen)
        except ParserError as e:
            raise Error(str(e))
        self.line_num += 1
        return row

    def next(self):
        # for python 2
        return self.__next__()
