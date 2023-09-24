# -*- coding: utf-8 -*-

"""
Code for computing the pattern score.

Author: Gertjan van den Burg

"""

import collections
import re

from typing import Optional
from typing import Pattern

from .cabstraction import base_abstraction
from .cabstraction import c_merge_with_quotechar
from .dialect import SimpleDialect

DEFAULT_EPS_PAT: float = 1e-3

RE_MULTI_C: Pattern[str] = re.compile(r"C{2,}")


def pattern_score(
    data: str, dialect: SimpleDialect, eps: float = DEFAULT_EPS_PAT
) -> float:
    """
    Compute the pattern score for given data and a dialect.

    Parameters
    ----------

    data : str
        The data of the file as a raw character string

    dialect: dialect.Dialect
        The dialect object

    Returns
    -------
    score : float
        the pattern score

    """
    A = make_abstraction(data, dialect)
    row_patterns = collections.Counter(A.split("R"))
    P = 0.0
    for pat_k, Nk in row_patterns.items():
        Lk = len(pat_k.split("D"))
        P += Nk * (max(eps, Lk - 1) / Lk)
    P /= len(row_patterns)
    return P


def make_abstraction(data: str, dialect: SimpleDialect) -> str:
    """Create an abstract representation of the CSV file based on the dialect.

    This function constructs the basic abstraction used to compute the row
    patterns.

    Parameters
    ----------
    data : str
        The data of the file as a string.

    dialect : SimpleDialect
        A dialect to parse the file with.

    Returns
    -------
    abstraction : str
        An abstract representation of the CSV file.

    """
    A = base_abstraction(
        data, dialect.delimiter, dialect.quotechar, dialect.escapechar
    )
    A = merge_with_quotechar(A)
    A = fill_empties(A)
    A = strip_trailing(A)
    return A


def merge_with_quotechar(
    S: str, dialect: Optional[SimpleDialect] = None
) -> str:
    """Merge quoted blocks in the abstraction

    This function takes the abstract representation and merges quoted blocks
    (``QC...CQ``) to a single cell (``C``). The function takes nested quotes
    into account.

    Parameters
    ----------
    S : str
        The data of a file as a string

    dialect : SimpleDialect
        The dialect used to make the abstraction. This is not used but kept for
        backwards compatibility. Will be removed in a future version.

    Returns
    -------
    abstraction : str
        A simplified version of the abstraction with quoted blocks merged.

    """
    return c_merge_with_quotechar(S)


def fill_empties(abstract: str) -> str:
    """Fill empty cells in the abstraction

    The way the row patterns are constructed assumes that empty cells are
    marked by the letter `C` as well. This function fill those in. The function
    also removes duplicate occurrances of ``CC`` and replaces these  with
    ``C``.

    Parameters
    ----------
    abstract : str
        The abstract representation of the file.

    Returns
    -------
    abstraction : str
        The abstract representation with empties filled.


    """
    while "DD" in abstract:
        abstract = abstract.replace("DD", "DCD")

    while "DR" in abstract:
        abstract = abstract.replace("DR", "DCR")

    while "RD" in abstract:
        abstract = abstract.replace("RD", "RCD")

    abstract = RE_MULTI_C.sub("C", abstract)

    if abstract.startswith("D"):
        abstract = "C" + abstract

    if abstract.endswith("D"):
        abstract += "C"

    return abstract


def strip_trailing(abstract: str) -> str:
    """Strip trailing row separator from abstraction."""
    while abstract.endswith("R"):
        abstract = abstract[:-1]
    return abstract
