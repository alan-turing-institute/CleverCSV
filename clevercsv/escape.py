# -*- coding: utf-8 -*-

"""
Common functions for dealing with escape characters.

Author: Gertjan van den Burg
Date: 2018-11-06
"""

import codecs
import sys
import unicodedata

from typing import Iterable
from typing import Optional
from typing import Set

#: Set of default characters to *never* consider as escape character
DEFAULT_BLOCK_CHARS: Set[str] = set(
    [
        "!",
        "?",
        '"',
        "'",
        ".",
        ",",
        ";",
        ":",
        "%",
        "*",
        "&",
        "#",
    ]
)

#: Set of characters in the Unicode "Po" category
UNICODE_PO_CHARS: Set[str] = set(
    [
        c
        for c in map(chr, range(sys.maxunicode + 1))
        if unicodedata.category(c) == "Po"
    ]
)


def is_potential_escapechar(
    char: str, encoding: str, block_char: Optional[Iterable[str]] = None
) -> bool:
    """Check if a character is a potential escape character.

    A character is considered a potential escape character if it is in the
    "Punctuation, Other" Unicode category and not in the list of blocked
    characters.

    Parameters
    ----------
    char: str
        The character to check

    encoding : str
        The encoding of the character

    block_char : Optional[Iterable[str]]
        Characters that are in the Punctuation Other category but that should
        not be considered as escape character. If None, the default set is
        used, which is defined in :py:data:`DEFAULT_BLOCK_CHARS`.

    Returns
    -------
    is_escape : bool
        Whether the character is considered a potential escape or not.

    """
    if encoding.lower() in set(["utf-8", "ascii"]):
        uchar = char
    else:
        uchar = codecs.decode(bytes(char, encoding), encoding=encoding)

    block_chars = (
        DEFAULT_BLOCK_CHARS if block_char is None else set(block_char)
    )
    if uchar in UNICODE_PO_CHARS and uchar not in block_chars:
        return True
    return False
