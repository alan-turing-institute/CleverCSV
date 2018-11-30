# -*- coding: utf-8 -*-

"""
Detect the dialect using the data consistency measure.

Author: Gertjan van den Burg

"""

from .potential_dialects import get_dialects
from .detect_pattern import pattern_score
from .detect_type import type_score
from .break_ties import tie_breaker


def detect_dialect_consistency(data, delimiters=None):
    dialects = get_dialects(data, delimiters=delimiters)
    Qmax = -float("inf")

    H = set()

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

    if len(H) == 1:
        return H.pop()
    return tie_breaker(data, list(H))
