# -*- coding: utf-8 -*-

"""
Drop-in replacement for the Python csv reader class. This is a wrapper for the
Parser class, defined in :mod:`cparser`.

Author: Gertjan van den Burg

"""

import csv

from typing import Any
from typing import Iterable
from typing import Iterator
from typing import List
from typing import Optional

from . import field_size_limit
from ._types import _DialectLike
from .cparser import Error as ParserError
from .cparser import Parser
from .dialect import SimpleDialect
from .exceptions import Error


class reader:
    def __init__(
        self,
        csvfile: Iterable[str],
        dialect: _DialectLike = "excel",
        **fmtparams: Any,
    ):
        self.csvfile = csvfile
        self.original_dialect = dialect
        self._dialect = self._make_simple_dialect(dialect, **fmtparams)
        self.line_num: int = 0
        self.parser_gen: Optional[Parser] = None

    @property
    def dialect(self) -> csv.Dialect:
        return self._dialect.to_csv_dialect()

    def _make_simple_dialect(
        self, dialect: _DialectLike, **fmtparams: Any
    ) -> SimpleDialect:
        if isinstance(dialect, str):
            sd = SimpleDialect.from_csv_dialect(csv.get_dialect(dialect))
        elif isinstance(dialect, csv.Dialect):
            sd = SimpleDialect.from_csv_dialect(dialect)
        elif isinstance(dialect, SimpleDialect):
            sd = dialect
        else:
            raise ValueError("Unknown dialect type: %r" % dialect)
        for key, value in fmtparams.items():
            if key in ["delimiter", "quotechar", "escapechar", "strict"]:
                setattr(sd, key, value)
        sd.validate()
        return sd

    def __iter__(self) -> Iterator[List[str]]:
        self.parser_gen = Parser(
            self.csvfile,
            delimiter=self._dialect.delimiter,
            quotechar=self._dialect.quotechar,
            escapechar=self._dialect.escapechar,
            field_limit=field_size_limit(),
            strict=self._dialect.strict,
        )
        return self

    def __next__(self) -> List[str]:
        if self.parser_gen is None:
            self.__iter__()
        assert self.parser_gen is not None
        try:
            row = next(self.parser_gen)
        except ParserError as e:
            raise Error(str(e))
        self.line_num += 1
        return row
