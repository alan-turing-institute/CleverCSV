# -*- coding: utf-8 -*-

"""
Python utility functions that wrap the C parser.

"""

import io

from typing import Any
from typing import Iterable
from typing import Iterator
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

from .cparser import Error as ParserError
from .cparser import Parser
from .dialect import SimpleDialect
from .exceptions import Error

_FIELD_SIZE_LIMIT: int = 128 * 1024


def field_size_limit(*args: Any, **kwargs: Any) -> int:
    """Get/Set the limit to the field size.

    This function is adapted from the one in the Python CSV module. See the
    documentation there.
    """
    global _FIELD_SIZE_LIMIT
    old_limit = _FIELD_SIZE_LIMIT
    all_args = list(args) + list(kwargs.values())
    if not 0 <= len(all_args) <= 1:
        raise TypeError(
            "field_size_limit expected at most 1 arguments, got %i"
            % len(all_args)
        )
    if len(all_args) == 0:
        return old_limit
    limit = all_args[0]
    if not isinstance(limit, int):
        raise TypeError("limit must be an integer")
    _FIELD_SIZE_LIMIT = int(limit)
    return old_limit


def _parse_data(
    data: Iterable[str],
    delimiter: str,
    quotechar: str,
    escapechar: str,
    strict: bool,
    return_quoted: bool = False,
) -> Iterator[Union[List[str], List[Tuple[str, bool]]]]:
    parser = Parser(
        data,
        delimiter=delimiter,
        quotechar=quotechar,
        escapechar=escapechar,
        field_limit=field_size_limit(),
        strict=strict,
        return_quoted=return_quoted,
    )
    try:
        for row in parser:
            yield row
    except ParserError as e:
        raise Error(str(e))


def parse_data(
    data: Iterable[str],
    dialect: Optional[SimpleDialect] = None,
    delimiter: Optional[str] = None,
    quotechar: Optional[str] = None,
    escapechar: Optional[str] = None,
    strict: Optional[bool] = None,
    return_quoted: bool = False,
) -> Iterator[Union[List[str], List[Tuple[str, bool]]]]:
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
    Error : clevercsv.exceptions.Error
        When an error occurs during parsing.

    """
    if dialect is None:
        dialect = SimpleDialect("", "", "")

    delimiter_ = delimiter if delimiter is not None else dialect.delimiter
    quotechar_ = quotechar if quotechar is not None else dialect.quotechar
    escapechar_ = escapechar if escapechar is not None else dialect.escapechar
    strict_ = strict if strict is not None else dialect.strict

    yield from _parse_data(
        data,
        delimiter_,
        quotechar_,
        escapechar_,
        strict_,
        return_quoted=return_quoted,
    )


def parse_string(
    data: str,
    dialect: SimpleDialect,
    return_quoted: bool = False,
) -> Iterator[Union[List[str], List[Tuple[str, bool]]]]:
    """Utility for when the CSV file is encoded as a single string"""
    return parse_data(
        iter(io.StringIO(data, newline="")),
        dialect=dialect,
        return_quoted=return_quoted,
    )
