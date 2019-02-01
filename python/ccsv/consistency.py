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
    dialects = get_dialects(data, delimiters=delimiters)
    Qmax = -float("inf")

    H = set()

    old_limit = field_size_limit(len(data) + 1)

    for dialect in sorted(dialects):
        P = pattern_score(data, dialect)
        if P < Qmax:
            continue
        T = type_score(data, dialect)
        Q = P * T
        if Q > Qmax:
            H = set([dialect])
            Qmax = Q
        elif Q == Qmax:
            H.add(dialect)

        if verbose:
            print("%15r:\tT = %.6f\tP = %.6f\tQ = %.6f" % (dialect, T, P, Q))

    if len(H) == 1:
        result = H.pop()
    else:
        result = tie_breaker(data, list(H))

    field_size_limit(old_limit)
    return result
