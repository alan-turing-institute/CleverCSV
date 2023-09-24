#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Drop-in replacement for the Python csv writer class.

Author: Gertjan van den Burg

"""

from __future__ import annotations

import csv

from typing import TYPE_CHECKING
from typing import Any
from typing import Iterable
from typing import Type

if TYPE_CHECKING:
    from clevercsv._types import SupportsWrite

from clevercsv._types import _DialectLike

from .dialect import SimpleDialect
from .exceptions import Error

DIALECT_KEYS = [
    "skipinitialspace",
    "doublequote",
    "strict",
    "delimiter",
    "escapechar",
    "lineterminator",
    "quotechar",
    "quoting",
]


class writer:
    def __init__(
        self,
        csvfile: SupportsWrite[str],
        dialect: _DialectLike = "excel",
        **fmtparams: Any,
    ) -> None:
        self.original_dialect = dialect
        self.dialect: Type[csv.Dialect] = self._make_python_dialect(
            dialect, **fmtparams
        )
        self._writer = csv.writer(csvfile, dialect=self.dialect)

    def _make_python_dialect(
        self, dialect: _DialectLike, **fmtparams: Any
    ) -> Type[csv.Dialect]:
        d: _DialectLike = ""
        if isinstance(dialect, str):
            d = csv.get_dialect(dialect)
        elif isinstance(dialect, csv.Dialect):
            d = dialect
        elif isinstance(dialect, SimpleDialect):
            d = dialect.to_csv_dialect()
        elif dialect in [csv.excel, csv.excel_tab, csv.unix_dialect]:
            d = dialect
        else:
            raise ValueError(f"Unknown dialect type: {dialect}")

        # Override properties from format parameters
        props = {k: getattr(d, k) for k in DIALECT_KEYS if hasattr(d, k)}
        for key, value in fmtparams.items():
            props[key] = value

        # lineterminator must be set
        if "lineterminator" not in props or props["lineterminator"] is None:
            props["lineterminator"] = "\n"

        # We have to subclass the csv.Dialect
        newdialect = type("dialect", (csv.Dialect,), props)
        return newdialect

    def writerow(self, row: Iterable[Any]) -> Any:
        try:
            return self._writer.writerow(row)
        except csv.Error as e:
            raise Error(str(e))

    def writerows(self, rows: Iterable[Iterable[Any]]) -> Any:
        try:
            return self._writer.writerows(rows)
        except csv.Error as e:
            raise Error(str(e))
