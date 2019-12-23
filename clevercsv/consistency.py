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

    # Get potential dialects
    dialects = get_dialects(data, delimiters=delimiters)
    return detect_consistency_dialects(data, dialects, verbose=verbose)


def detect_consistency_dialects(data, dialects, verbose=False):
    """Wrapper for dialect detection with the consistency measure

    This function takes a list of dialects to consider.
    """
    log = lambda *a, **kw: print(*a, **kw) if verbose else None
    log("Considering %i dialects." % len(dialects))

    old_limit = field_size_limit(len(data) + 1)
    scores = consistency_scores(data, dialects, skip=True, logger=log)
    H = get_best_set(scores)
    result = break_ties(data, H)
    field_size_limit(old_limit)

    return result


def consistency_scores(data, dialects, skip=True, logger=print):
    scores = {}

    Qmax = -float("inf")
    for dialect in sorted(dialects):
        P = pattern_score(data, dialect)
        if P < Qmax and skip:
            scores[dialect] = {"pattern": P, "type": None, "Q": None}
            logger("%15r:\tP = %15.6f\tskip." % (dialect, P))
            continue
        T = type_score(data, dialect)
        Q = P * T
        Qmax = max(Q, Qmax)
        scores[dialect] = {"pattern": P, "type": T, "Q": Q}
        logger(
            "%15r:\tP = %15.6f\tT = %15.6f\tQ = %15.6f" % (dialect, P, T, Q)
        )
    return scores


def get_best_set(scores):
    Qscores = [score["Q"] for score in scores.values()]
    Qscores = filter(lambda q: not q is None, Qscores)
    Qmax = max(Qscores)
    return set([d for d, score in scores.items() if score["Q"] == Qmax])


def break_ties(data, dialects):
    D = list(dialects)
    if len(dialects) == 1:
        return D[0]
    return tie_breaker(data, D)
