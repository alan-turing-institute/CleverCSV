# -*- coding: utf-8 -*-

"""
Detect the dialect using the data consistency measure.

Author: Gertjan van den Burg

"""

from . import field_size_limit
from .break_ties import tie_breaker
from .detect_pattern import pattern_score
from .detect_type import type_score
from .potential_dialects import get_dialects


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

    # wrapper for the print function
    log = lambda *a, **kw: print(*a, **kw) if verbose else None

    # Get potential dialects
    dialects = get_dialects(data, delimiters=delimiters)
    log("Considering %i dialects." % len(dialects))
    Qmax = -float("inf")

    H = set()

    # increase the field size limit to the max expected
    old_limit = field_size_limit(len(data) + 1)

    for dialect in sorted(dialects):
        P = pattern_score(data, dialect)
        if P < Qmax:
            log("%15r:\tP = %15.6f\tskip." % (dialect, P))
            continue
        T = type_score(data, dialect)
        Q = P * T
        if Q > Qmax:
            H = set([dialect])
            Qmax = Q
        elif Q == Qmax:
            H.add(dialect)

        log("%15r:\tP = %15.6f\tT = %15.6f\tQ = %15.6f" % (dialect, P, T, Q))

    if len(H) == 1:
        result = H.pop()
    else:
        result = tie_breaker(data, list(H))

    field_size_limit(old_limit)
    return result


def consistency_scores(data, dialects, skip=True):
    scores = {}

    Qmax = -float("inf")
    for dialect in sorted(dialects):
        P = pattern_score(data, dialect)
        if P < Qmax and skip:
            scores[dialect] = {
                "pattern": P,
                "type": float("nan"),
                "Q": float("nan"),
            }
            continue
        T = type_score(data, dialect)
        Q = P * T
        Qmax = max(Q, Qmax)
        scores[dialect] = {"pattern": P, "type": T, "Q": Q}
    return scores
