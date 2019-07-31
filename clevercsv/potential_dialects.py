# -*- coding: utf-8 -*-

"""
Code for selecting the potential dialects of a file.

Author: Gertjan van den Burg

"""

import codecs
import itertools
import regex
import unicodedata

from .dialect import SimpleDialect
from .escape import is_potential_escapechar
from .utils import pairwise


def get_dialects(data, encoding="UTF-8", delimiters=None):
    """Return the possible dialects for the given data.

    We consider as escape characters those characters for which 
    is_potential_escapechar() is True and that occur at least once before a 
    quote character or delimiter in the dialect.

    One may wonder if self-escaping is an issue here (i.e. "\\\\", two times 
    backslash). It is not. In a file where a single backslash is desired and 
    escaping with a backslash is used, then it only makes sense to do this in a 
    file where the backslash is already used as an escape character (in which 
    case we include it). If it is never used as escape for the delimiter or 
    quotechar, then it is not necessary to self-escape. This is an assumption, 
    but it holds in general and it reduces noise.

    Parameters
    ----------
    data: str
        The data for the file

    encoding: str
        The encoding of the file

    delimiters: iterable
        Set of delimiters to consider. See :func:`get_delimiters` for more 
        info.

    Returns
    -------
    dialects: list
        List of SimpleDialect objects that are considered potential dialects.

    """
    # URLs are removed to reduce noise
    no_url = filter_urls(data)
    delims = get_delimiters(no_url, encoding, delimiters=delimiters)
    quotechars = get_quotechars(no_url)
    escapechars = {}

    for delim, quotechar in itertools.product(delims, quotechars):
        escapechars[(delim, quotechar)] = set([""])

    # escapechars are those that precede a delimiter or quotechar
    for u, v in pairwise(data):
        if not is_potential_escapechar(u, encoding):
            continue
        for delim, quotechar in itertools.product(delims, quotechars):
            if v == delim or v == quotechar:
                escapechars[(delim, quotechar)].add(u)

    # remove dialects where the delimiter is always masked by quotes.
    dialects = []
    for delim in delims:
        for quotechar in quotechars:
            for escapechar in escapechars[(delim, quotechar)]:
                if masked_by_quotechar(data, quotechar, escapechar, delim):
                    continue
                d = SimpleDialect(delim, quotechar, escapechar)
                dialects.append(d)
    return dialects


def unicode_category(x, encoding=None):
    """Return the Unicode category of a character

    Parameters
    ----------
    x : str
        character

    encoding: str
        Encoding of the character

    Returns
    -------
    category: str
        The Unicode category of the character.

    """
    as_unicode = codecs.decode(bytes(x, encoding), encoding=encoding)
    return unicodedata.category(as_unicode)


def filter_urls(data):
    """Filter URLs from the data """
    pat = "(?:(?:[A-Za-z]{3,9}:(?:\/\/)?)(?:[-;:&=\+\$,\w]+@)?[A-Za-z0-9.-]+|(?:www.|[-;:&=\+\$,\w]+@)[A-Za-z0-9.-]+)(?:(?:\/[\+~%\/.\w\-_]*)?\??(?:[-\+=&;%@.\w_]*)#?(?:[\w]*))?"
    return regex.sub(pat, "U", data, count=0)


def get_delimiters(
    data, encoding, delimiters=None, block_cat=None, block_char=None
):
    """Get potential delimiters

    The set of potential delimiters is constructed as follows. For each unique 
    character of the file, we check if its Unicode character category is in the 
    set ``block_cat`` of prohibited categories.  If it is, we don't allow it to 
    be a delimiter, with the exception of Tab (which is in the Control 
    category).  We furthermore block characters in :attr:`block_char` from 
    being delimiters. 

    Parameters
    ----------
    data: str
        The data of the file

    encoding: str
        The encoding of the file

    delimiters: iterable
        Allowed delimiters. If provided, it overrides the block_cat/block_char 
        mechanism and only the provided characters will be considered 
        delimiters (if they occur in the file). If None, all characters can be 
        considered delimiters subject to the :attr:`block_cat` and 
        :attr:`block_char` parameters.

    block_cat: list
        List of Unicode categories (2-letter abbreviations) for characters that 
        should not be considered as delimiters. If None, the following default 
        set is used::

        ["Lu", "Ll", "Lt", "Lm", "Lo", "Nd", "Nl", "No", "Ps", "Pe", "Co"]

    block_char: list
        Explicit list of characters that should not be considered delimiters.
        If None, the following default set is used::

        [".", "/", '"', "'", "\\n", "\\r"]


    Returns
    -------
    delims: set
        Set of potential delimiters. The empty string is added by default.

    """
    if block_cat is None:
        block_cat = [
            "Lu",
            "Ll",
            "Lt",
            "Lm",
            "Lo",
            "Nd",
            "Nl",
            "No",
            "Ps",
            "Pe",
            "Co",
        ]
    if block_char is None:
        block_char = [".", "/", '"', "'", "\n", "\r"]

    D = set()
    for x in set(data):
        c = unicode_category(x, encoding=encoding)
        if delimiters is None:
            if x == "\t" or ((x not in block_char) and (c not in block_cat)):
                D.add(x)
        else:
            if x in delimiters:
                D.add(x)
    D.add("")
    return D


def get_quotechars(data, quote_chars=None):
    """Get potential quote characters

    Quote characters are those that occur in the ``quote_chars`` set and are 
    found at least once in the file.

    Parameters
    ----------

    data: str
        The data of the file as a string

    quote_chars: iterable
        Characters that should be considered quote characters. If it is None, 
        the following default set is used::

        ["'", '"', "~", "`"]


    Returns
    -------
    quotes: set
        Set of potential quote characters. The empty string is added by 
        default.

    """
    if quote_chars is None:
        quote_chars = ["'", '"', "~", "`"]
    Q = set(quote_chars) & set(data)
    Q.add("")
    return Q


def masked_by_quotechar(data, quotechar, escapechar, test_char):
    """Test if a character is always masked by quote characters

    This function tests if a given character is always within quoted segments 
    (defined by the quote character). Double quoting and escaping is supported.

    Parameters
    ----------
    data: str
        The data of the file as a string

    quotechar: str
        The quote character

    escapechar: str
        The escape character

    test_char: str
        The character to test

    Returns
    -------
    masked: bool
        Returns True if the test character is never outside quoted segements, 
        False otherwise.

    """
    if test_char == "":
        return False
    escape_next = False
    in_quotes = False
    i = 0
    while i < len(data):
        s = data[i]
        if s == quotechar:
            if escape_next:
                i += 1
                continue
            if not in_quotes:
                in_quotes = True
            else:
                if i + 1 < len(data) and data[i + 1] == quotechar:
                    i += 1
                else:
                    in_quotes = False
        elif s == test_char and not in_quotes:
            return False
        elif s == escapechar:
            escape_next = True
        i += 1
    return True
