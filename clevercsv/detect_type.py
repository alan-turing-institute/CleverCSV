# -*- coding: utf-8 -*-

"""
Code for computing the type score.

Author: Gertjan van den Burg

"""

import regex

from .cparser_util import parse_string

DEFAULT_EPS_TYPE = 1e-10

# Used this site: https://unicode-search.net/unicode-namesearch.pl
SPECIALS_ALLOWED = [
    # Periods
    "\u002e",
    "\u06d4",
    "\u3002",
    "\ufe52",
    "\uff0e",
    "\uff61",
    # Parentheses
    "\u0028",
    "\u0029",
    "\u27ee",
    "\u27ef",
    "\uff08",
    "\uff09",
    # Question marks
    "\u003F",
    "\u00BF",
    "\u037E",
    "\u055E",
    "\u061F",
    "\u1367",
    "\u1945",
    "\u2047",
    "\u2048",
    "\u2049",
    "\u2CFA",
    "\u2CFB",
    "\u2E2E",
    "\uA60F",
    "\uA6F7",
    "\uFE16",
    "\uFE56",
    "\uFF1F",
    chr(69955),  # chakma question mark
    chr(125279),  # adlam initial question mark
    # Exclamation marks
    "\u0021",
    "\u00A1",
    "\u01C3",
    "\u055C",
    "\u07F9",
    "\u109F",
    "\u1944",
    "\u203C",
    "\u2048",
    "\u2049",
    "\uAA77",
    "\uFE15",
    "\uFE57",
    "\uFF01",
    chr(125278),  # adlam initial exclamation mark
]

PATTERNS = {
    "number_1": "^(?=[+-\.\d])[+-]?(?:0|[1-9]\d*)?(((?P<dot>((?<=\d)\.|\.(?=\d)))?(?(dot)(?P<yes_dot>\d*(\d*[eE][+-]?\d+)?)|(?P<no_dot>((?<=\d)[eE][+-]?\d+)?)))|((?P<comma>,)?(?(comma)(?P<yes_comma>\d+(\d+[eE][+-]?\d+)?)|(?P<no_comma>((?<=\d)[eE][+-]?\d+)?))))$",
    "number_2": "[+-]?(?:[1-9]|[1-9]\d{0,2})(?:\,\d{3})+\.\d*",
    "number_3": "[+-]?(?:[1-9]|[1-9]\d{0,2})(?:\.\d{3})+\,\d*",
    "url": "(?:(?:[A-Za-z]{3,9}:(?:\/\/)?)(?:[-;:&=\+\$,\w]+@)?[A-Za-z0-9.-]+|(?:www.|[-;:&=\+\$,\w]+@)[A-Za-z0-9.-]+)(?:(?:\/[\+~%\/.\w\-_]*)?\??(?:[-\+=&;%@.\w_]*)#?(?:[\w]*))?",
    "email": r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)",
    "unicode_alphanum": "(\p{N}?\p{L}+[\p{N}\p{L}\ "
    + regex.escape("".join(SPECIALS_ALLOWED))
    + "]*|\p{L}?[\p{N}\p{L}\ "
    + regex.escape("".join(SPECIALS_ALLOWED))
    + "]+)",
    "time_hhmmss": "(0[0-9]|1[0-9]|2[0-3]):([0-5][0-9]):([0-5][0-9])",
    "time_hhmm": "(0[0-9]|1[0-9]|2[0-3]):([0-5][0-9])",
    "time_HHMM": "(0[0-9]|1[0-9]|2[0-3])([0-5][0-9])",
    "time_HH": "(0[0-9]|1[0-9]|2[0-3])([0-5][0-9])",
    "time_hmm": "([0-9]|1[0-9]|2[0-3]):([0-5][0-9])",
    "currency": "\p{Sc}\s?(.*)",
    "unix_path": "[\/~]{1,2}(?:[a-zA-Z0-9\.]+(?:[\/]{1,2}))?(?:[a-zA-Z0-9\.]+)",
    "date": "((0[1-9]|1[0-2])((0[1-9]|[12]\d|3[01])([12]\d{3}|\d{2})|(?P<sep1>[-\/. ])(0?[1-9]|[12]\d|3[01])(?P=sep1)([12]\d{3}|\d{2}))|(0[1-9]|[12]\d|3[01])((0[1-9]|1[0-2])([12]\d{3}|\d{2})|(?P<sep2>[-\/. ])(0?[1-9]|1[0-2])(?P=sep2)([12]\d{3}|\d{2}))|([12]\d{3}|\d{2})((?P<sep3>[-\/. ])(0?[1-9]|1[0-2])(?P=sep3)(0?[1-9]|[12]\d|3[01])|年(0?[1-9]|1[0-2])月(0?[1-9]|[12]\d|3[01])日|년(0?[1-9]|1[0-2])월(0?[1-9]|[12]\d|3[01])일|(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01]))|(([1-9]|1[0-2])(?P<sep4>[-\/. ])(0?[1-9]|[12]\d|3[01])(?P=sep4)([12]\d{3}|\d{2})|([1-9]|[12]\d|3[01])(?P<sep5>[-\/. ])(0?[1-9]|1[0-2])(?P=sep5)([12]\d{3}|\d{2})))",
}


class TypeDetector(object):
    def __init__(self, strip_whitespace=True):
        self.patterns = PATTERNS.copy()
        self.strip_whitespace = strip_whitespace
        self._compile_regexes()

    def _compile_regexes(self):
        for key, value in self.patterns.items():
            self.patterns[key] = regex.compile(value)

    def is_known_type(self, cell):
        return not self.detect_type(cell) is None

    def detect_type(self, cell):
        type_tests = [
            ("empty", self.is_empty),
            ("url_or_email", self.is_url_or_email),
            ("number", self.is_number),
            ("time", self.is_time),
            ("percentage", self.is_percentage),
            ("currency", self.is_currency),
            ("unicode_alphanum", self.is_unicode_alphanum),
            ("unix_path", self.is_unix_path),
            ("nan", self.is_nan),
            ("date", self.is_date),
            ("datetime", self.is_datetime),
        ]
        for name, func in type_tests:
            if func(cell):
                return name
        return None

    def _run_regex(self, cell, patname):
        if self.strip_whitespace:
            cell = cell.strip(" ")
        pat = self.patterns.get(patname, None)
        match = pat.fullmatch(cell)
        return match is not None

    def is_number(self, cell):
        if cell == "":
            return False
        if self._run_regex(cell, "number_1"):
            return True
        if self._run_regex(cell, "number_2"):
            return True
        if self._run_regex(cell, "number_3"):
            return True
        return False

    def is_url_or_email(self, cell):
        return self._run_regex(cell, "url") or self._run_regex(cell, "email")

    def is_unicode_alphanum(self, cell):
        return self._run_regex(cell, "unicode_alphanum")

    def is_date(self, cell):
        # This function assumes the cell is not a number.
        if not cell:
            return False
        if not cell[0].isdigit():
            return False
        return self._run_regex(cell, "date")

    def is_time(self, cell):
        if not cell:
            return False
        if not cell[0].isdigit():
            return False
        return (
            self._run_regex(cell, "time_hmm")
            or self._run_regex(cell, "time_hhmm")
            or self._run_regex(cell, "time_hhmmss")
        )

    def is_empty(self, cell):
        if self.strip_whitespace:
            cell = cell.strip(" ")
        return cell == ""

    def is_percentage(self, cell):
        if self.strip_whitespace:
            cell = cell.strip(" ")
        return cell.endswith("%") and self.is_number(cell.rstrip("%"))

    def is_currency(self, cell):
        if self.strip_whitespace:
            cell = cell.strip(" ")
        pat = self.patterns.get("currency", None)
        m = pat.fullmatch(cell)
        if m is None:
            return False
        grp = m.group(1)
        if not self.is_number(grp):
            return False
        return True

    def is_datetime(self, cell):
        # Takes care of cells with '[date] [time]' and '[date]T[time]' (iso)
        if not cell:
            return False
        if not cell[0].isdigit():
            return False
        if " " in cell:
            parts = cell.split(" ")
            if len(parts) > 2:
                return False
            return self.is_date(parts[0]) and self.is_time(parts[1])
        elif "T" in cell:
            parts = cell.split("T")
            if len(parts) > 2:
                return False
            isdate = self.is_date(parts[0])
            if not isdate:
                return False
            # [date]T[time]
            if self.is_time(parts[1]):
                return True
            # [date]T[time][+-][time]
            if "+" in parts[1]:
                subparts = parts[1].split("+")
                istime1 = self.is_time(subparts[0])
                istime2 = self.is_time(subparts[1])
                if not istime1:
                    return False
                if istime2:
                    return True
                if self._run_regex(subparts[1], "time_HHMM"):
                    return True
                if self._run_regex(subparts[1], "time_HH"):
                    return True
            elif "-" in parts[1]:
                subparts = parts[1].split("-")
                istime1 = self.is_time(subparts[0])
                istime2 = self.is_time(subparts[1])
                if not istime1:
                    return False
                if istime2:
                    return True
                if self._run_regex(subparts[1], "time_HHMM"):
                    return True
                if self._run_regex(subparts[1], "time_HH"):
                    return True
        return False

    def is_nan(self, cell):
        if self.strip_whitespace:
            cell = cell.strip(" ")
        # other forms (na and nan) are caught by unicode_alphanum
        if cell.lower() == "n/a":
            return True
        return False

    def is_unix_path(self, cell):
        if self.strip_whitespace:
            cell = cell.strip(" ")
        return self._run_regex(cell, "unix_path")


def gen_known_type(cells):
    """
    Utility that yields a generator over whether or not the provided cells are 
    of a known type or not.
    """
    td = TypeDetector()
    for cell in cells:
        yield td.is_known_type(cell)


def type_score(data, dialect, eps=DEFAULT_EPS_TYPE):
    """
    Compute the type score as the ratio of cells with a known type.

    Parameters
    ----------
    data: str
        the data as a single string

    dialect: SimpleDialect
        the dialect to use

    eps: float
        the minimum value of the type score

    """
    total = 0
    known = 0
    td = TypeDetector()
    for row in parse_string(data, dialect):
        for cell in row:
            total += 1
            known += td.is_known_type(cell)
    if total == 0:
        return eps
    return max(eps, known / total)
