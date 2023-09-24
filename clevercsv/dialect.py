#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Definitions for the dialect object.

Author: Gertjan van den Burg

"""

import csv
import functools
import json

from typing import Any
from typing import Dict
from typing import Optional
from typing import Tuple
from typing import Type
from typing import Union

excel = csv.excel
excel_tab = csv.excel_tab
unix_dialect = csv.unix_dialect


@functools.total_ordering
class SimpleDialect:
    """
    The simplified dialect object.

    For the delimiter, quotechar, and escapechar the empty string means no
    delimiter/quotechar/escapechar in the file. None is used to mark it
    undefined.

    Parameters
    ----------
    delimiter : str
        The delimiter of the CSV file.

    quotechar : str
        The quotechar of the file.

    escapechar : str
        The escapechar of the file.

    strict : bool
        Whether strict parsing should be enforced. Same as in the csv module.

    """

    def __init__(
        self,
        delimiter: Optional[str],
        quotechar: Optional[str],
        escapechar: Optional[str],
        strict: bool = False,
    ):
        self.delimiter = delimiter
        self.quotechar = quotechar
        self.escapechar = escapechar
        self.strict = strict

    def validate(self) -> None:
        if self.delimiter is None or len(self.delimiter) > 1:
            raise ValueError(
                "Delimiter should be zero or one characters, got: %r"
                % self.delimiter
            )
        if self.quotechar is None or len(self.quotechar) > 1:
            raise ValueError(
                "Quotechar should be zero or one characters, got: %r"
                % self.quotechar
            )
        if self.escapechar is None or len(self.escapechar) > 1:
            raise ValueError(
                "Escapechar should be zero or one characters, got: %r"
                % self.escapechar
            )
        if self.strict not in set([False, True]):
            raise ValueError(
                "Strict should be True or False, got: %r" % self.strict
            )

    @classmethod
    def from_dict(
        cls: Type["SimpleDialect"], d: Dict[str, Any]
    ) -> "SimpleDialect":
        dialect = cls(
            d["delimiter"], d["quotechar"], d["escapechar"], strict=d["strict"]
        )
        return dialect

    @classmethod
    def from_csv_dialect(
        cls: Type["SimpleDialect"], d: csv.Dialect
    ) -> "SimpleDialect":
        delimiter = "" if d.delimiter is None else d.delimiter
        quotechar = "" if d.quoting == csv.QUOTE_NONE else d.quotechar
        escapechar = "" if d.escapechar is None else d.escapechar
        return cls(delimiter, quotechar, escapechar, strict=d.strict)

    def to_csv_dialect(self) -> csv.Dialect:
        class dialect(csv.Dialect):
            assert self.delimiter is not None
            delimiter = self.delimiter
            quotechar = '"' if self.quotechar == "" else self.quotechar
            escapechar = None if self.escapechar == "" else self.escapechar
            doublequote = True
            quoting = (
                csv.QUOTE_NONE if self.quotechar == "" else csv.QUOTE_MINIMAL
            )
            skipinitialspace = False
            # TODO: We need to set this because it can't be None anymore in
            # recent versions of Python
            lineterminator = "\n"

        return dialect()

    def to_dict(self) -> Dict[str, Union[str, bool, None]]:
        self.validate()
        d = dict(
            delimiter=self.delimiter,
            quotechar=self.quotechar,
            escapechar=self.escapechar,
            strict=self.strict,
        )
        return d

    def serialize(self) -> str:
        """Serialize dialect to a JSON object"""
        return json.dumps(self.to_dict())

    @classmethod
    def deserialize(cls: Type["SimpleDialect"], obj: str) -> "SimpleDialect":
        """Deserialize dialect from a JSON object"""
        return cls.from_dict(json.loads(obj))

    def __repr__(self) -> str:
        return "SimpleDialect(%r, %r, %r)" % (
            self.delimiter,
            self.quotechar,
            self.escapechar,
        )

    def __key(
        self,
    ) -> Tuple[Optional[str], Optional[str], Optional[str], bool]:
        return (self.delimiter, self.quotechar, self.escapechar, self.strict)

    def __hash__(self) -> int:
        return hash(self.__key())

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, SimpleDialect):
            return False
        return self.__key() == other.__key()

    def __lt__(self, other: Any) -> bool:
        # This provides a partial order on dialect objects with the goal of
        # speeding up the consistency measure.
        if not isinstance(other, SimpleDialect):
            return False
        if self.delimiter == "," and not other.delimiter == ",":
            return True
        elif other.delimiter == "," and not self.delimiter == ",":
            return False
        if self.delimiter == ";" and not other.delimiter == ";":
            return True
        elif other.delimiter == ";" and not self.delimiter == ";":
            return False
        return self.__key() < other.__key()
