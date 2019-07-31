# -*- coding: utf-8 -*-

"""
Common functions for dealing with escape characters.

Author: Gertjan van den Burg
Date: 2018-11-06
"""

import codecs
import unicodedata


def is_potential_escapechar(char, encoding, block_char=None):
    """Check if a character is a potential escape character.

    A character is considered a potential escape character if it is in the 
    "Punctuation, Other" Unicode category and in the list of blocked 
    characters.

    Parameters
    ----------
    char: str
        The character to check

    encoding : str
        The encoding of the character

    block_char : iterable
        Characters that are in the Punctuation Other category but that should 
        not be considered as escape character. If None, the default set is 
        used, equal to::

        ["!", "?", '"', "'", ".", ",", ";", ":", "%", "*", "&", "#"

    Returns
    -------
    is_escape : bool
        Whether the character is considered a potential escape or not.

    """
    as_unicode = codecs.decode(bytes(char, encoding), encoding=encoding)

    ctr = unicodedata.category(as_unicode)
    if block_char is None:
        block_char = [
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
    if ctr == "Po":
        if as_unicode in block_char:
            return False
        return True
    return False
