# -*- coding: utf-8 -*-

"""
Python utility functions that wrap the C parser.

"""

import io

from .cparser import Parser, Error as ParserError
from .dialect import SimpleDialect
from .exceptions import Error

_FIELD_SIZE_LIMIT = 128 * 1024

def field_size_limit(*args, **kwargs):
    """Get/Set the limit to the field size.

    This function is adapted from the one in the Python CSV module. See the 
    documentation there.
    """
    global _FIELD_SIZE_LIMIT
    old_limit = _FIELD_SIZE_LIMIT
    args = list(args) + list(kwargs.values())
    if not 0 <= len(args) <= 1:
        raise TypeError(
            "field_size_limit expected at most 1 arguments, got %i" % len(args)
        )
    if len(args) == 0:
        return old_limit
    limit = args[0]
    if not isinstance(limit, int):
        raise TypeError("limit must be an integer")
    _FIELD_SIZE_LIMIT = int(limit)
    return old_limit


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
    try:
        for row in parser:
            yield row
    except ParserError as e:
        raise Error(str(e))


def parse_string(data, *args, **kwargs):
    """ Utility for when the CSV file is encoded as a single string """
    return parse_data(io.StringIO(data, newline=""), *args, **kwargs)
