# -*- coding: utf-8 -*-

"""
Translation of the Python FSM for reading CSV files, amended version.

This parser automatically takes double quotes into account, and can sensibly 
deal with quotes that start *inside* a cell.  Quotes are only stripped from 
cells if they occur at the start and the end of the cell.

Author: Gertjan van den Burg
Date: 2019-01-23

"""

import enum
import io
import six

from .dialect import SimpleDialect
from .exceptions import Error

_FIELD_SIZE_LIMIT = 128 * 1024

class State(enum.Enum):
    START_RECORD = 0
    START_FIELD = 1
    ESCAPED_CHAR = 2
    IN_FIELD = 3
    IN_QUOTED_FIELD = 4
    ESCAPE_IN_QUOTED_FIELD = 5
    QUOTE_IN_QUOTED_FIELD = 6
    EAT_CRNL = 7
    AFTER_ESCAPED_CRNL = 8



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

def unicode_check(x):
    if six.PY2:
        return isinstance(x, unicode) or isinstance(x, str)
    return isinstance(x, str)


def pairwise_none(iterable):
    it1 = iter(iterable)
    it2 = iter(iterable)
    next(it2, None)
    for s in it1:
        t = next(it2, None)
        yield s, t



class Parser(object):
    def __init__(self, dialect):
        self.dialect = dialect
        self.records = []
        self.state = None

    def reset(self):
        self.fields = []
        self.field = None
        self.field_len = 0
        self.state = State.START_RECORD

    def parse(self, data):
        self.reset()
        self.input_iter = iter(data)

        while True:
            fields = self.parse_iternext()
            if fields is None:
                break
            yield fields

    def parse_iternext(self):
        self.reset()
        while True:
            line = next(self.input_iter, None)
            if line is None:
                if self.field_len != 0 or self.state == State.IN_QUOTED_FIELD:
                    if self.dialect.strict:
                        raise Error("unexpected end of data")
                    self.parse_save_field(trailing=True)
                    break
                return None
            if not unicode_check(line):
                raise Error(
                    "iterator should return strings, not %.200s "
                    "(did you open the file in text mode?)"
                    % type(line).__name__
                )
            for u, v in pairwise_none(line):
                if u == "\0":
                    raise Error("line contains NULL byte")
                self.parse_process_char(u, v)
            self.parse_process_char("\0", None)
            if self.state == State.START_RECORD:
                break

        return self.fields

    def parse_process_char(self, u, v):
        if self.state == State.START_RECORD:
            fallthru, retcode = self._start_record(u)
            if fallthru:
                self._start_field(u)
        elif self.state == State.START_FIELD:
            retcode = self._start_field(u)
        elif self.state == State.ESCAPED_CHAR:
            retcode = self._escaped_char(u)
        elif self.state == State.AFTER_ESCAPED_CRNL:
            fallthru, retcode = self._after_escaped_crnl(u)
            if fallthru:
                self._in_field(u)
        elif self.state == State.IN_FIELD:
            retcode = self._in_field(u)
        elif self.state == State.IN_QUOTED_FIELD:
            retcode = self._in_quoted_field(u, v)
        elif self.state == State.ESCAPE_IN_QUOTED_FIELD:
            retcode = self._escape_in_quoted_field(u)
        elif self.state == State.QUOTE_IN_QUOTED_FIELD:
            retcode = self._quote_in_quoted_field(u)
        elif self.state == State.EAT_CRNL:
            retcode = self._eat_crnl(u)

        return retcode

    def parse_add_char(self, u):
        if self.field_len >= _FIELD_SIZE_LIMIT:
            raise Error(
                "field larger than field limit (%d)" % _FIELD_SIZE_LIMIT
            )
        if self.field is None:
            self.field = []
        self.field.append(u)
        self.field_len += 1
        return 0

    def quote_condition(self, s):
        """ Check if a string starts and ends with the quote character """
        if not self.dialect.quotechar:
            return False
        if len(s) <= 1:
            return False
        return s.startswith(self.dialect.quotechar) and s.endswith(
            self.dialect.quotechar
        )

    def parse_save_field(self, trailing=False):
        if self.field is None:
            field = ''
        else:
            field = ''.join(self.field)
        if self.quote_condition(field):
            field = field[1:-1]
        if (
            trailing
            and self.dialect.quotechar
            and field.startswith(self.dialect.quotechar)
        ):
            field = field[1:]
        self.fields.append(field)
        # In CPython, characters are added using field_len as index, so
        # resetting the field is not necessary. We do have to do it though.
        self.field = None
        self.field_len = 0
        return 0

    def _start_record(self, u):
        # Returns fallthru and return code
        if u == "\0":
            return False, 0
        elif u == "\r" or u == "\n":
            self.state = State.EAT_CRNL
            return False, 0
        self.state = State.START_FIELD
        return True, 0

    def _start_field(self, u):
        if u == "\r" or u == "\n" or u == "\0":
            self.parse_save_field()
            self.state = State.START_RECORD if u == "\0" else State.EAT_CRNL
        elif u == self.dialect.quotechar:
            self.parse_add_char(u)
            self.state = State.IN_QUOTED_FIELD
        elif u == self.dialect.escapechar:
            self.state = State.ESCAPED_CHAR
        elif u == self.dialect.delimiter:
            self.parse_save_field()
        else:
            self.parse_add_char(u)
            self.state = State.IN_FIELD
        return 0

    def _escaped_char(self, u):
        if u == "\r" or u == "\n":
            self.parse_add_char(u)
            self.state = State.AFTER_ESCAPED_CRNL
            return 0
        # only escape "escapable" characters.
        if not u in [
            self.dialect.escapechar,
            self.dialect.delimiter,
            self.dialect.quotechar,
            "\0",
        ]:
            self.parse_add_char(self.dialect.escapechar)
        if u == "\0":
            u = ""
        self.parse_add_char(u)
        self.state = State.IN_FIELD
        return 0

    def _after_escaped_crnl(self, u):
        # Returns fallthru and return code
        if u == "\0":
            return False, 0
        return True, 0

    def _in_field(self, u):
        if u == "\r" or u == "\n" or u == "\0":
            # EOL return [fields]
            self.parse_save_field()
            self.state = State.START_RECORD if u == "\0" else State.EAT_CRNL
        elif u == self.dialect.escapechar:
            self.state = State.ESCAPED_CHAR
        elif u == self.dialect.quotechar:
            self.parse_add_char(u)
            self.state = State.IN_QUOTED_FIELD
        elif u == self.dialect.delimiter:
            self.parse_save_field()
            self.state = State.START_FIELD
        else:
            self.parse_add_char(u)
        return 0

    def _in_quoted_field(self, u, v):
        if u == "\0":
            pass
        elif u == self.dialect.escapechar:
            self.state = State.ESCAPE_IN_QUOTED_FIELD
        elif u == self.dialect.quotechar:
            if v == self.dialect.quotechar:
                self.dialect.doublequote = True
                self.state = State.QUOTE_IN_QUOTED_FIELD
            elif self.dialect.strict:
                raise Error(
                    "'%c' expected after '%c'"
                    % (self.dialect.delimiter, self.dialect.quotechar)
                )
            else:
                self.parse_add_char(u)
                self.state = State.IN_FIELD
        else:
            self.parse_add_char(u)
        return 0

    def _escape_in_quoted_field(self, u):
        # only escape "escapable" characters.
        if not u in [
            self.dialect.escapechar,
            self.dialect.delimiter,
            self.dialect.quotechar,
            "\0",
        ]:
            self.parse_add_char(self.dialect.escapechar)
        if u == "\0":
            u = ""
        self.parse_add_char(u)
        self.state = State.IN_QUOTED_FIELD
        return 0

    def _quote_in_quoted_field(self, u):
        if u == self.dialect.quotechar:
            self.parse_add_char(u)
            self.state = State.IN_QUOTED_FIELD
        elif u == self.dialect.delimiter:
            self.parse_save_field()
            self.state = State.START_FIELD
        elif u == "\r" or u == "\n" or u == "\0":
            self.parse_save_field()
            self.state = State.START_RECORD if u == "\0" else State.EAT_CRNL
        elif not self.dialect.strict:
            self.parse_add_char(u)
            self.state = State.IN_FIELD
        else:
            raise Error(
                "'%c' expected after '%c'"
                % (self.dialect.delimiter, self.dialect.quotechar)
            )
        return 0

    def _eat_crnl(self, u):
        if u == "\r" or u == "\n":
            return 0
        elif u == "\0":
            self.state = State.START_RECORD
        else:
            raise Error("new-line character seen in unquoted field.")
        return 0


def parse_data(
    data, dialect=None, delimiter=None, quotechar=None, escapechar=None
):
    if dialect is None:
        dialect = SimpleDialect("", "", "")
    if not delimiter is None:
        dialect.delimiter = delimiter
    if not quotechar is None:
        dialect.quotechar = quotechar
    if not escapechar is None:
        dialect.escapechar = escapechar

    parser = Parser(dialect)
    for row in parser.parse(data):
        yield row


def parse_string(data, *args, **kwargs):
    """ Utility for when the CSV file is encoded as a single string """
    return parse_data(io.StringIO(data, newline=""), *args, **kwargs)
