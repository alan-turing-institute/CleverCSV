#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Definitions for the dialect

Author: Gertjan van den Burg

"""

import csv
import functools


@functools.total_ordering
class SimpleDialect(object):
    """
    The simplified dialect object.
    """

    def __init__(self, delimiter, quotechar, escapechar, strict=False):
        self.delimiter = delimiter
        self.quotechar = quotechar
        self.escapechar = escapechar
        self.strict = strict

    def validate(self):
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
        if not self.strict in [False, True]:
            raise ValueError(
                "Strict should be True or False, got: %r" % self.strict
            )

    @classmethod
    def from_dict(cls, d):
        d = cls(
            d["delimiter"], d["quotechar"], d["escapechar"], strict=d["strict"]
        )
        return d

    @classmethod
    def from_csv_dialect(cls, d):
        delimiter = "" if d.delimiter is None else d.delimiter
        quotechar = "" if d.quotechar is None else d.quotechar
        escapechar = "" if d.escapechar is None else d.escapechar
        return cls(delimiter, quotechar, escapechar, strict=d.strict)

    def to_csv_dialect(self):
        class dialect(csv.Dialect):
            delimiter = self.delimiter
            quotechar = self.quotechar
            escapechar = self.escapechar
            doublequote = True
            quoting = csv.QUOTE_MINIMAL

        return dialect

    def to_dict(self):
        self.validate()
        d = dict(
            delimiter=self.delimiter,
            quotechar=self.quotechar,
            escapechar=self.escapechar,
            strict=self.strict,
        )
        return d

    def __repr__(self):
        return "SimpleDialect(%r, %r, %r)" % (
            self.delimiter,
            self.quotechar,
            self.escapechar,
        )

    def __key(self):
        return (self.delimiter, self.quotechar, self.escapechar, self.strict)

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        if not isinstance(other, SimpleDialect):
            return False
        return self.__key() == other.__key()

    def __lt__(self, other):
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
