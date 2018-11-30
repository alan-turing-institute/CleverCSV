#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Drop-in replacement for the Python csv reader class.

Author: Gertjan van den Burg

"""

import csv

from .dialect import SimpleDialect
from .parser import parse_data


class reader(object):
    def __init__(self, csvfile, dialect="excel", **fmtparams):
        self.csvfile = csvfile
        self.original_dialect = dialect

        if isinstance(dialect, str):
            self.dialect = get_simple_dialect_from_string(dialect)
        elif isinstance(dialect, csv.Dialect):
            self.dialect = convert_to_simple(dialect)
        else:
            self.dialect = dialect

        update_dialect_with_fmtparams(self.dialect, fmtparams)

    def __iter__(self):
        yield from parse_data(self.csvfile, self.dialect)


def get_simple_dialect_from_string(dialect_string):
    if dialect_string == "excel":
        return SimpleDialect(delimiter=",", quotechar='"', escapechar="")


def convert_to_simple(dialect):
    pass


def update_dialect_with_fmtparams(dialect, fmtparams):
    pass
