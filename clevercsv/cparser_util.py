# -*- coding: utf-8 -*-

"""
Python utility functions that wrap the C parser.

"""

import io

from .cparser import Error as ParserError
from .cparser import Parser
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
    data,
    dialect=None,
    delimiter=None,
    quotechar=None,
    escapechar=None,
    strict=None,
    return_quoted=False,
):
    """Parse the data given a dialect using the C parser

    Parameters
    ----------
    data : iterable
        The data of the CSV file as an iterable

    dialect : SimpleDialect
        The dialect to use for the parsing. If None, the dialect with each
        component set to the empty string is used.

    delimiter : str
        The delimiter to use. If not None, overwrites the delimiter in the
        dialect.

    quotechar : str
        The quote character to use. If not None, overwrites the quote character
        in the dialect.

    escapechar : str
        The escape character to use. If not None, overwrites the escape
        character in the dialect.

    strict : bool
        Enable strict mode or not. If not None, overwrites the strict mode set
        in the dialect.

    return_quoted : bool
        For each cell, return a tuple "(field, is_quoted)" where the second
        element indicates whether the cell was a quoted cell or not.

    Yields
    ------
    rows : list
        The rows of the file as a list of cells.

    Raises
    ------
    Error
        When an error occurs during parsing.

    """
    if dialect is None:
        dialect = SimpleDialect("", "", "")

    delimiter_ = delimiter if not delimiter is None else dialect.delimiter
    quotechar_ = quotechar if not quotechar is None else dialect.quotechar
    escapechar_ = escapechar if not escapechar is None else dialect.escapechar
    strict_ = strict if not strict is None else dialect.strict

    parser = Parser(
        data,
        delimiter=delimiter_,
        quotechar=quotechar_,
        escapechar=escapechar_,
        field_limit=field_size_limit(),
        strict=strict_,
        return_quoted=return_quoted,
    )
    try:
        for row in parser:
            yield row
    except ParserError as e:
        raise Error(str(e))


def parse_string(data, *args, **kwargs):
    """Utility for when the CSV file is encoded as a single string"""
    return parse_data(io.StringIO(data, newline=""), *args, **kwargs)
