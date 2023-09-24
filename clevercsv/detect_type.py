# -*- coding: utf-8 -*-

"""
Code for computing the type score.

Author: Gertjan van den Burg

"""

import json

from typing import Dict
from typing import List
from typing import Optional
from typing import Pattern

from ._regexes import DEFAULT_TYPE_REGEXES
from .cparser_util import parse_string
from .dialect import SimpleDialect

DEFAULT_EPS_TYPE: float = 1e-10


class TypeDetector:
    def __init__(
        self,
        patterns: Optional[Dict[str, Pattern[str]]] = None,
        strip_whitespace: bool = True,
    ) -> None:
        self.patterns = patterns or DEFAULT_TYPE_REGEXES.copy()
        self.strip_whitespace = strip_whitespace
        self._register_type_tests()

    def _register_type_tests(self) -> None:
        self._type_tests = [
            ("empty", self.is_empty),
            ("url", self.is_url),
            ("email", self.is_email),
            ("ipv4", self.is_ipv4),
            ("number", self.is_number),
            ("time", self.is_time),
            ("percentage", self.is_percentage),
            ("currency", self.is_currency),
            ("unix_path", self.is_unix_path),
            ("nan", self.is_nan),
            ("date", self.is_date),
            ("datetime", self.is_datetime),
            ("unicode_alphanum", self.is_unicode_alphanum),
            ("bytearray", self.is_bytearray),
            ("json", self.is_json_obj),
        ]

    def list_known_types(self) -> List[str]:
        return [tt[0] for tt in self._type_tests]

    def is_known_type(self, cell: str, is_quoted: bool = False) -> bool:
        return self.detect_type(cell, is_quoted=is_quoted) is not None

    def detect_type(self, cell: str, is_quoted: bool = False) -> Optional[str]:
        cell = cell.strip() if self.strip_whitespace else cell
        for name, func in self._type_tests:
            if func(cell, is_quoted=is_quoted):
                return name
        return None

    def _run_regex(self, cell: str, patname: str) -> bool:
        cell = cell.strip() if self.strip_whitespace else cell
        pat = self.patterns.get(patname, None)
        assert pat is not None
        match = pat.fullmatch(cell)
        return match is not None

    def is_number(self, cell: str, is_quoted: bool = False) -> bool:
        if cell == "":
            return False
        if self._run_regex(cell, "number_1"):
            return True
        if self._run_regex(cell, "number_2"):
            return True
        if self._run_regex(cell, "number_3"):
            return True
        return False

    def is_ipv4(self, cell: str, is_quoted: bool = False) -> bool:
        return self._run_regex(cell, "ipv4")

    def is_url(self, cell: str, is_quoted: bool = False) -> bool:
        return self._run_regex(cell, "url")

    def is_email(self, cell: str, is_quoted: bool = False) -> bool:
        return self._run_regex(cell, "email")

    def is_unicode_alphanum(self, cell: str, is_quoted: bool = False) -> bool:
        if is_quoted:
            return self._run_regex(cell, "unicode_alphanum_quoted")
        return self._run_regex(cell, "unicode_alphanum")

    def is_date(self, cell: str, is_quoted: bool = False) -> bool:
        # This function assumes the cell is not a number.
        cell = cell.strip() if self.strip_whitespace else cell
        if not cell:
            return False
        if not cell[0].isdigit():
            return False
        return self._run_regex(cell, "date")

    def is_time(self, cell: str, is_quoted: bool = False) -> bool:
        cell = cell.strip() if self.strip_whitespace else cell
        if not cell:
            return False
        if not cell[0].isdigit():
            return False
        return (
            self._run_regex(cell, "time_hmm")
            or self._run_regex(cell, "time_hhmm")
            or self._run_regex(cell, "time_hhmmss")
            or self._run_regex(cell, "time_hhmmsszz")
        )

    def is_empty(self, cell: str, is_quoted: bool = False) -> bool:
        return cell == ""

    def is_percentage(self, cell: str, is_quoted: bool = False) -> bool:
        return cell.endswith("%") and self.is_number(cell.rstrip("%"))

    def is_currency(self, cell: str, is_quoted: bool = False) -> bool:
        pat = self.patterns.get("currency", None)
        assert pat is not None
        m = pat.fullmatch(cell)
        if m is None:
            return False
        grp = m.group(1)
        if not self.is_number(grp):
            return False
        return True

    def is_datetime(self, cell: str, is_quoted: bool = False) -> bool:
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
            # [date]T[time] or [date]T[time]Z
            if parts[1].endswith("Z") and self.is_time(parts[1][:-1]):
                return True
            if self.is_time(parts[1]):
                return True
            # [date]T[time][+-][time]
            if "+" in parts[1]:
                subparts = parts[1].split("+")
                istime1 = self.is_time(subparts[0])
                if not istime1:
                    return False
                istime2 = self.is_time(subparts[1])
                if istime2:
                    return True
                if self._run_regex(subparts[1], "time_HHMM"):
                    return True
                if self._run_regex(subparts[1], "time_HH"):
                    return True
            elif "-" in parts[1]:
                subparts = parts[1].split("-")
                istime1 = self.is_time(subparts[0])
                if not istime1:
                    return False
                istime2 = self.is_time(subparts[1])
                if istime2:
                    return True
                if self._run_regex(subparts[1], "time_HHMM"):
                    return True
                if self._run_regex(subparts[1], "time_HH"):
                    return True
        return False

    def is_nan(self, cell: str, is_quoted: bool = False) -> bool:
        if cell.lower() in ["n/a", "na", "nan"]:
            return True
        return False

    def is_unix_path(self, cell: str, is_quoted: bool = False) -> bool:
        return self._run_regex(cell, "unix_path")

    def is_bytearray(self, cell: str, is_quoted: bool = False) -> bool:
        return cell.startswith("bytearray(b") and cell.endswith(")")

    def is_json_obj(self, cell: str, is_quoted: bool = False) -> bool:
        if not (cell.startswith("{") and cell.endswith("}")):
            return False
        try:
            _ = json.loads(cell)
        except json.JSONDecodeError:
            return False
        return True


def gen_known_type(cells):
    """
    Utility that yields a generator over whether or not the provided cells are
    of a known type or not.
    """
    td = TypeDetector()
    for cell in cells:
        yield td.is_known_type(cell)


def type_score(
    data: str, dialect: SimpleDialect, eps: float = DEFAULT_EPS_TYPE
) -> float:
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

    Returns
    -------
    type_score: float
        The computed type score

    """
    total = 0
    known = 0
    td = TypeDetector()
    for row in parse_string(data, dialect, return_quoted=True):
        for cell, is_quoted in row:
            total += 1
            known += td.is_known_type(cell, is_quoted=is_quoted)
    if total == 0:
        return eps
    return max(eps, known / total)
