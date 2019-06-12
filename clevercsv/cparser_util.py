# -*- coding: utf-8 -*-

"""
Python utility functions that wrap the C parser.

"""

import io

from .cparser import Parser
from .dialect import SimpleDialect
from .parser import field_size_limit


def parse_data(
    iterable, dialect=None, delimiter=None, quotechar=None, escapechar=None
):
    """
    Parse iterable given dialect. Wraps the C parser.

    """
    if dialect is None:
        dialect = SimpleDialect("", "", "")
    if not delimiter is None:
        dialect.delimiter = delimiter
    if not quotechar is None:
        dialect.quotechar = quotechar
    if not escapechar is None:
        dialect.escapechar = escapechar

    parser = Parser(
        iterable,
        delimiter=dialect.delimiter,
        quotechar=dialect.quotechar,
        escapechar=dialect.escapechar,
        field_limit=field_size_limit(),
    )
    for row in parser:
        yield row


def parse_string(data, *args, **kwargs):
    """ Utility for when the CSV file is encoded as a single string """
    return parse_data(io.StringIO(data, newline=""), *args, **kwargs)
