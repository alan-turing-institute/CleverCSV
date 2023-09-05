# -*- coding: utf-8 -*-

"""
Break ties in the data consistency measure.

Author: Gertjan van den Burg

"""

from typing import List
from typing import Optional

from .cparser_util import parse_string
from .dialect import SimpleDialect
from .utils import pairwise


def tie_breaker(
    data: str, dialects: List[SimpleDialect]
) -> Optional[SimpleDialect]:
    """
    Break ties between dialects.

    This function is used to break ties where possible between two, three, or
    four dialects that receive the same value for the data consistency measure.

    Parameters
    ----------
    data: str
        The data as a single string
    dialects: list
        Dialects that are tied

    Returns
    -------
    dialect: SimpleDialect
        One of the dialects from the list provided or None.


    """
    if len(dialects) == 2:
        return break_ties_two(data, dialects[0], dialects[1])
    elif len(dialects) == 3:
        return break_ties_three(data, dialects[0], dialects[1], dialects[2])
    elif len(dialects) == 4:
        return break_ties_four(data, dialects)
    return None


def reduce_pairwise(
    data: str, dialects: List[SimpleDialect]
) -> Optional[List[SimpleDialect]]:
    """Reduce the set of dialects by breaking pairwise ties

    Parameters
    ----------

    data: str
        The data of the file as a string

    dialects: list
        List of SimpleDialect objects

    Returns
    -------
    dialects: list
        List of SimpleDialect objects.

    """
    equal_delim = len(set([d.delimiter for d in dialects])) == 1
    if not equal_delim:
        return None  # TODO: This might be wrong, it can just return the input!

    # First, identify dialects that result in the same parsing result.
    equal_dialects = []
    for a, b in pairwise(dialects):
        X = list(parse_string(data, a))
        Y = list(parse_string(data, b))
        if X == Y:
            equal_dialects.append((a, b))

    # Try to break the ties in these pairs
    new_dialects = set()
    visited = set()
    for A, B in equal_dialects:
        ans = break_ties_two(data, A, B)
        if ans is not None:
            new_dialects.add(ans)
        visited.add(A)
        visited.add(B)

    # and add the dialects that we didn't visit
    for d in dialects:
        if d not in visited:
            new_dialects.add(d)

    return list(new_dialects)


def _dialects_only_differ_in_field(
    A: SimpleDialect, B: SimpleDialect, field: str
) -> bool:
    keys = ["delimiter", "quotechar", "escapechar"]
    return all(
        getattr(A, key) == getattr(B, key) for key in keys if key != field
    )


def break_ties_two(
    data: str, A: SimpleDialect, B: SimpleDialect
) -> Optional[SimpleDialect]:
    """Break ties between two dialects.

    This function breaks ties between two dialects that give the same score. We
    distinguish several cases:

    1. If delimiter and escapechar are the same and one of the quote characters
    is the empty string. We parse the file with both dialects and check if the
    parsing result is the same. If it is, the correct dialect is the one with
    no quotechar, otherwise it's the other one.
    2. If quotechar and escapechar are the same and the delimiters are comma
    and space, then we go for comma. Alternatively, if either of the delimiters
    is the hyphen, we assume it's the other dialect.
    3. If the delimiter and quotechar is the same and one dialect uses the
    escapchar and the other doesn't. We break this tie by checking if the
    escapechar has an effect and if it occurs an even or odd number of times.

    If it's none of these cases, we don't break the tie and return None.

    Parameters
    ----------

    data: str
        The data of the file as a string.

    A: SimpleDialect
        A potential dialect

    B: SimpleDialect
        A potential dialect

    Returns
    -------

    dialect: SimpleDialect or None
        The chosen dialect if the tie can be broken, None otherwise.

    """
    if _dialects_only_differ_in_field(A, B, "quotechar"):
        if A.quotechar == "" or B.quotechar == "":
            d_no = A if A.quotechar == "" else B
            d_yes = B if d_no == A else A

            X = list(parse_string(data, dialect=d_no))
            Y = list(parse_string(data, dialect=d_yes))

            if X == Y:
                # quotechar has no effect
                return d_no
            else:
                # quotechar has an effect
                return d_yes
    elif _dialects_only_differ_in_field(A, B, "delimiter"):
        if set([A.delimiter, B.delimiter]) == set([",", " "]):
            # Artifact due to type detection (comma as radix point)
            if A.delimiter == ",":
                return A
            else:
                return B
        elif A.delimiter == "-" or B.delimiter == "-":
            # Artifact due to type detection (dash as minus sign)
            if A.delimiter == "-":
                return B
            else:
                return A
    elif _dialects_only_differ_in_field(A, B, "escapechar"):
        Dnone, Descape = (A, B) if A.escapechar == "" else (B, A)

        X = list(parse_string(data, Dnone))
        Y = list(parse_string(data, Descape))

        # double check shape. Usually if the shape differs the pattern score
        # should have caught it, but if by a freakish occurance it hasn't then
        # we can't break this tie (for now)
        if len(X) != len(Y):
            return None
        for row_X, row_Y in zip(X, Y):
            if len(row_X) != len(row_Y):
                return None

        cells_escaped = []
        cells_unescaped = []
        for row_X, row_Y in zip(X, Y):
            for u, v in zip(row_X, row_Y):
                if u != v:
                    cells_unescaped.append(u)
                    cells_escaped.append(v)

        # We will break the ties in the following ways:
        #
        # If the escapechar precedes the quotechar an even number of times
        # within each offending cell, then we think it is a functional escape
        # and the escaped version is the correct dialect. Note that if an odd
        # number of escaped quotechars would occur, then the shape of the file
        # will be different if it is ignored. Only if it occurs an even number
        # of times within the cell can we get the same shape.
        for u in cells_unescaped:
            count = 0
            for a, b in pairwise(u):
                if a != Descape.escapechar:
                    continue
                if a == Descape.escapechar and b == Descape.quotechar:
                    count += 1
            if count > 0 and count % 2 == 0:
                return Descape
            else:
                return Dnone
    elif A.delimiter == B.delimiter:
        Aq, Ae = A.quotechar, A.escapechar
        Bq, Be = B.quotechar, B.escapechar
        if (Aq, Ae) == ("", "") or (Bq, Be) == ("", ""):
            # This case is activated if the escapechar+quotechar combination
            # occurs in the cells (i.e. "Jill\'s data") but no actual quoting
            # is done with the quote character.
            d_no = A if (Aq, Ae) == ("", "") else B
            d_yes = B if d_no == A else A

            X = list(parse_string(data, dialect=d_no))
            Y = list(parse_string(data, dialect=d_yes))

            if len(X) != len(Y):
                return None
            for row_X, row_Y in zip(X, Y):
                if len(row_X) != len(row_Y):
                    return None

            # if we're here, then there is no effect on structure.
            # we test if the only cells that differ are those that have an
            # escapechar+quotechar combination.
            assert isinstance(d_yes.escapechar, str)
            assert isinstance(d_yes.quotechar, str)
            eq = d_yes.escapechar + d_yes.quotechar
            for row_X, row_Y in zip(X, Y):
                for x, y in zip(row_X, row_Y):
                    if x != y:
                        if eq not in x:
                            return None

            # Now we know that the only cells that have the
            # escapechar+quotechar combination are the cause of the difference.
            # The right thing to do is to return the dialect that uses them.
            return d_yes

    return None


def break_ties_three(
    data: str, A: SimpleDialect, B: SimpleDialect, C: SimpleDialect
) -> Optional[SimpleDialect]:
    """Break ties between three dialects.

    If the delimiters and the escape characters are all equal, then we look for
    the dialect that has no quotechar. The tie is broken by calling
    :func:`break_ties_two` for the dialect without quotechar and another
    dialect that gives the same parsing result.

    If only the delimiter is the same for all dialects then use
    :func:`break_ties_two` on the dialects that do not have a quotechar,
    provided there are only two of these.

    Parameters
    ----------

    data: str
        The data of the file as a string

    A: SimpleDialect
        a dialect

    B: SimpleDialect
        a dialect

    C: SimpleDialect
        a dialect

    Returns
    -------

    dialect: Optional[SimpleDialect]
        The chosen dialect if the tie can be broken, None otherwise.

    Notes
    -----
    We have only observed one tie for each case during development, so
    this may need to be improved in the future.

    """

    equal_delim = A.delimiter == B.delimiter == C.delimiter
    equal_escape = A.escapechar == B.escapechar == C.escapechar

    if equal_delim and equal_escape:
        # difference is *only* in quotechar
        dialects = [A, B, C]

        pA = list(parse_string(data, A))
        pB = list(parse_string(data, B))
        pC = list(parse_string(data, C))

        if len(pA) != len(pB) or len(pA) != len(pC) or len(pB) != len(pC):
            return None

        p_none, d_none = next(
            (
                (p, d)
                for p, d in zip([pA, pB, pC], dialects)
                if d.quotechar == ""
            ),
            (None, None),
        )
        if p_none is None:
            return None
        assert d_none is not None

        rem = [
            (p, d) for p, d in zip([pA, pB, pC], dialects) if not p == p_none
        ]

        if len(rem) <= 1:
            # This case was reached for the file
            # 6da5ab459bcc7c3a5ed2e06d65810958.csv from the GitHub corpus of
            # the CSV paper. When fixing the delimiter to Tab, rem = [].
            # Try to reduce pairwise
            new_dialects = reduce_pairwise(data, dialects)
            if new_dialects is None:
                return None
            if len(new_dialects) == 1:
                return new_dialects[0]
            return None
        if p_none == rem[0][0]:
            return break_ties_two(data, d_none, rem[0][1])
        elif len(rem) > 1 and p_none == rem[1][0]:
            return break_ties_two(data, d_none, rem[1][1])
    elif equal_delim:
        # difference is in quotechar *and* escapechar

        # The reasoning here is as follows. If we are in this situation,
        # then there is both a potential escapechar and there are quotechars,
        # but the pattern score is the same and the type score can't make a
        # difference because no cells become clean if we interpret the
        # quote/escape correctly. This implies that the quote and escape do
        # have a function. Thus, we find the dialects that have a quote and
        # defer to break_ties_two.

        dialects = [A, B, C]
        with_quote = [d for d in dialects if d.quotechar != ""]

        if len(with_quote) != 2:
            return None

        return break_ties_two(data, with_quote[0], with_quote[1])

    return None


def break_ties_four(
    data: str, dialects: List[SimpleDialect]
) -> Optional[SimpleDialect]:
    """Break ties between four dialects.

    This function works by breaking the ties between pairs of dialects that
    result in the same parsing result (if any). If this reduces the number of
    dialects, then :func:`break_ties_three` or :func:`break_ties_two` is used,
    otherwise, the tie can't be broken.

    Ties are only broken if all dialects have the same delimiter.

    Parameters
    ----------

    data: str
        The data of the file as a string

    dialects: list
        List of SimpleDialect objects

    Returns
    -------
    dialect: Optional[SimpleDialect]
        The chosen dialect if the tie can be broken, None otherwise.

    Notes
    -----
    We have only observed one case during development where this
    function was needed. It may need to be revisited in the future if other
    examples are found.

    """
    # TODO: Check for length 4, handle more than 4 too?

    equal_delim = len(set([d.delimiter for d in dialects])) == 1
    if not equal_delim:
        return None

    reduced_dialects = reduce_pairwise(data, dialects)
    if reduced_dialects is None:
        return None

    # Defer to other functions if the number of dialects was reduced
    if len(reduced_dialects) == 1:
        return reduced_dialects[0]
    elif len(reduced_dialects) == 2:
        return break_ties_two(data, *reduced_dialects)
    elif len(reduced_dialects) == 3:
        return break_ties_three(data, *reduced_dialects)

    return None
