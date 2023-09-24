# -*- coding: utf-8 -*-

"""
Detect the dialect with very strict functional tests.

This module uses so-called "normal forms" to detect the dialect of CSV files.
Normal forms are detected with strict functional tests. The normal forms are 
used as a pre-test to check if files are simple enough that computing the data 
consistency measure is not necessary.

Author: Gertjan van den Burg

"""

import itertools

from typing import Callable
from typing import Iterable
from typing import List
from typing import Optional
from typing import Tuple

import regex

from .dialect import SimpleDialect
from .escape import is_potential_escapechar
from .utils import pairwise

DELIMS: List[str] = [",", ";", "|", "\t"]
QUOTECHARS: List[str] = ["'", '"']


def detect_dialect_normal(
    data: str,
    encoding: str = "UTF-8",
    delimiters: Optional[Iterable[str]] = None,
    verbose: bool = False,
) -> Optional[SimpleDialect]:
    """Detect the normal form of a file from a given sample

    Parameters
    ----------
    data : str
        The data as a single string

    encoding : str
        The encoding of the data

    Returns
    -------
    dialect : SimpleDialect
        The dialect detected using normal forms, or None if no such dialect can
        be found.
    """
    if delimiters is None:
        delimiters = DELIMS
    delimiters = list(delimiters)
    for delim, quotechar in itertools.product(delimiters, QUOTECHARS):
        if maybe_has_escapechar(data, encoding, delim, quotechar):
            if verbose:
                print("Not normal, has potential escapechar.")
            return None

    form_and_dialect: List[
        Tuple[int, Callable[[str, SimpleDialect], bool], SimpleDialect]
    ] = []

    for delim in delimiters:
        dialect = SimpleDialect(delimiter=delim, quotechar="", escapechar="")
        form_and_dialect.append((2, is_form_2, dialect))

    for delim, quotechar in itertools.product(delimiters, QUOTECHARS):
        dialect = SimpleDialect(
            delimiter=delim, quotechar=quotechar, escapechar=""
        )
        form_and_dialect.append((1, is_form_1, dialect))
        form_and_dialect.append((3, is_form_3, dialect))
        form_and_dialect.append((5, is_form_5, dialect))
    for quotechar in QUOTECHARS:
        dialect = SimpleDialect(
            delimiter="", quotechar=quotechar, escapechar=""
        )
        form_and_dialect.append((4, is_form_4, dialect))

    form_and_dialect.append(
        (
            4,
            is_form_4,
            SimpleDialect(delimiter="", quotechar="", escapechar=""),
        )
    )

    for ID, form_func, dialect in form_and_dialect:
        if form_func(data, dialect):
            if verbose:
                print("Matched normal form %i." % ID)
            return dialect
    if verbose:
        print("Didn't match any normal forms.")
    return None


def is_quoted_cell(cell: str, quotechar: str) -> bool:
    if len(cell) < 2:
        return False
    return cell[0] == quotechar and cell[-1] == quotechar


def is_any_quoted_cell(cell: str) -> bool:
    return is_quoted_cell(cell, "'") or is_quoted_cell(cell, '"')


def is_any_partial_quoted_cell(cell: str) -> bool:
    if len(cell) < 1:
        return False
    return (
        cell[0] == '"' or cell[0] == "'" or cell[-1] == '"' or cell[-1] == "'"
    )


def is_empty_quoted(cell: str, quotechar: str) -> bool:
    return len(cell) == 2 and is_quoted_cell(cell, quotechar)


def is_empty_unquoted(cell: str) -> bool:
    return cell == ""


def is_any_empty(cell: str) -> bool:
    return (
        is_empty_unquoted(cell)
        or is_empty_quoted(cell, "'")
        or is_empty_quoted(cell, '"')
    )


def has_delimiter(string: str, delim: str) -> bool:
    return delim in string


def has_nested_quotes(string: str, quotechar: str) -> bool:
    return quotechar in string[1:-1]


def maybe_has_escapechar(
    data: str, encoding: str, delim: str, quotechar: str
) -> bool:
    if delim not in data and quotechar not in data:
        return False
    for u, v in pairwise(data):
        if v in [delim, quotechar] and is_potential_escapechar(u, encoding):
            return True
    return False


def strip_trailing_crnl(data: str) -> str:
    while data.endswith("\n"):
        data = data.rstrip("\n")
    while data.endswith("\r"):
        data = data.rstrip("\r")
    return data


def every_row_has_delim(rows: List[str], dialect: SimpleDialect) -> bool:
    assert dialect.delimiter is not None
    for row in rows:
        if not has_delimiter(row, dialect.delimiter):
            return False
    return True


def is_elementary(cell: str) -> bool:
    return (
        regex.fullmatch(r"[a-zA-Z0-9\.\_\&\-\@\+\%\(\)\ \/]+", cell)
        is not None
    )


def even_rows(rows: List[str], dialect: SimpleDialect) -> bool:
    cells_per_row = set()
    for row in rows:
        cells_per_row.add(len(split_row(row, dialect)))
    return len(cells_per_row) == 1


def split_file(data: str) -> List[str]:
    data = strip_trailing_crnl(data)
    if "\r\n" in data:
        return data.split("\r\n")
    elif "\n" in data:
        return data.split("\n")
    elif "\r" in data:
        return data.split("\r")
    return [data]


def split_row(row: str, dialect: SimpleDialect) -> List[str]:
    # no nested quotes
    assert dialect.quotechar is not None
    if (not dialect.quotechar) or (dialect.quotechar not in row):
        if not dialect.delimiter:
            return [row]
        return row.split(dialect.delimiter)

    cells = []
    current_cell = ""
    in_quotes = False
    for c in row:
        if c == dialect.delimiter and not in_quotes:
            cells.append(current_cell)
            current_cell = ""
        elif c == dialect.quotechar:
            in_quotes = not in_quotes
            current_cell += c
        else:
            current_cell += c
    if current_cell:
        cells.append(current_cell)
    return cells


def is_form_1(data: str, dialect: SimpleDialect) -> bool:
    # All cells quoted, quoted empty allowed, no nested quotes, more than one
    # column
    assert dialect.quotechar is not None

    rows = split_file(data)

    if not every_row_has_delim(rows, dialect):
        return False
    if not even_rows(rows, dialect):
        return False

    for row in rows:
        cells = split_row(row, dialect)
        if len(cells) == 1:
            return False
        for cell in cells:
            # No empty cells
            if is_empty_unquoted(cell):
                return False

            # All cells must be quoted
            if not is_quoted_cell(cell, dialect.quotechar):
                return False

            # No quotes inside quotes
            if has_nested_quotes(cell, dialect.quotechar):
                return False

    return True


def is_form_2(data: str, dialect: SimpleDialect) -> bool:
    # All unquoted, empty allowed, all elementary

    rows = split_file(data)

    if not every_row_has_delim(rows, dialect):
        return False
    if not even_rows(rows, dialect):
        return False

    for row in rows:
        cells = split_row(row, dialect)
        if len(cells) == 1:
            return False
        for cell in cells:
            # All cells must be unquoted
            if is_any_quoted_cell(cell):
                return False
            # All cells must not be partially quoted
            if is_any_partial_quoted_cell(cell):
                return False
            # Cells have to be elementary
            if not is_empty_unquoted(cell) and not is_elementary(cell):
                return False
    return True


def is_form_3(data: str, dialect: SimpleDialect) -> bool:
    # some quoted, some not quoted, no empty, no nested quotes
    assert dialect.quotechar is not None

    rows = split_file(data)

    if not every_row_has_delim(rows, dialect):
        return False
    if not even_rows(rows, dialect):
        return False
    if len(rows) <= 1:
        return False

    for row in rows:
        cells = split_row(row, dialect)
        if len(cells) == 1:
            return False
        for cell in cells:
            if is_any_empty(cell):
                return False

            # if it is quoted
            if is_any_quoted_cell(cell):
                # but not quoted with the quotechar of the dialect
                if not is_quoted_cell(cell, dialect.quotechar):
                    # then this form isn't right
                    return False
            # if it's not quoted
            else:
                # and it's not elementary
                if not is_elementary(cell):
                    # then this form isn't right
                    return False

    return True


def is_form_4(data: str, dialect: SimpleDialect) -> bool:
    # no delim, single column (either entirely quoted or entirely unquoted)
    assert dialect.quotechar is not None

    rows = split_file(data)

    if len(rows) <= 1:
        return False

    unquoted_search = regex.compile(r"[^A-Za-z0-9.\_&\-]").search
    quoted_search = regex.compile(r"[^A-Za-z0-9.\_&\-\ ]").search
    for row in rows:
        cell = row[:]
        if dialect.quotechar == "":
            if is_any_quoted_cell(cell):
                return False
            if unquoted_search(cell):
                return False
        else:
            if not is_quoted_cell(cell, dialect.quotechar):
                return False
            if quoted_search(cell[1:-1]):
                return False

    return True


def is_form_5(data: str, dialect: SimpleDialect) -> bool:
    # all rows quoted, no nested quotes
    # basically form 2 but with quotes around each row

    rows = split_file(data)

    if not every_row_has_delim(rows, dialect):
        return False
    if len(rows) <= 1:
        return False

    for row in rows:
        if not (
            len(row) > 2
            and row[0] == dialect.quotechar
            and row[-1] == dialect.quotechar
        ):
            return False

    newrows = []
    for row in rows:
        newrows.append(row[1:-1])

    return is_form_2("\n".join(newrows), dialect)
