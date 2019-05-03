# -*- coding: utf-8 -*-

"""
Detect the dialect using the data consistency measure.

Author: Gertjan van den Burg

"""

from .potential_dialects import get_dialects
from .detect_pattern import pattern_score
from .detect_type import type_score
from .break_ties import tie_breaker
from .parser import field_size_limit


def detect_dialect_consistency(data, delimiters=None, verbose=False):
    """Detect the dialect with the data consistency measure

    This uses the data consistency measure to detect the dialect. See the paper 
    for details.

    Parameters
    ----------
    data : str
        The data of the file as a string

    delimiters : iterable
        List of delimiters to consider. If None, the :func:`get_delimiters` 
        function is used to automatically detect this (as described in the 
        paper).

    verbose : bool
        Print out the dialects considered and their scores.

    Returns
    -------
    dialect : SimpleDialect
        The detected dialect. If no dialect could be detected, returns None.

    """

    dialects = get_dialects(data, delimiters=delimiters)
    if verbose:
        print("Considering %i dialects." % len(dialects))
    Qmax = -float("inf")

    H = set()

    old_limit = field_size_limit(len(data) + 1)

    for dialect in sorted(dialects):
        P = pattern_score(data, dialect)
        if P < Qmax:
            if verbose:
                print(
                    "%15r:\tP = %15.6f\tT = %15.6f\tQ = %15.6f"
                    % (dialect, P, float("nan"), float("nan"))
                )
            continue
        T = type_score(data, dialect)
        Q = P * T
        if Q > Qmax:
            H = set([dialect])
            Qmax = Q
        elif Q == Qmax:
            H.add(dialect)

        if verbose:
            print(
                "%15r:\tP = %15.6f\tT = %15.6f\tQ = %15.6f" % (dialect, P, T, Q)
            )

    if len(H) == 1:
        result = H.pop()
    else:
        result = tie_breaker(data, list(H))

    field_size_limit(old_limit)
    return result
