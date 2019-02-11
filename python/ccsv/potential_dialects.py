# -*- coding: utf-8 -*-

"""
Code for selecting the potential dialects for a given file.

Author: Gertjan van den Burg

"""

import codecs
import itertools
import regex
import six
import unicodedata

from .dialect import SimpleDialect
from .escape import is_potential_escapechar
from .utils import pairwise


def get_dialects(data, encoding="UTF-8", delimiters=None):
    """
    Return the possible dialects for the given data.

    We consider as escape characters those characters for which 
    is_potential_escapechar() is True and that occur at least once before a 
    quote character or delimiter in the dialect.

    One may wonder if self-escaping is an issue here (i.e. "\\\\", two times 
    backslash). It is not. In a file where a single backslash is desired and 
    escaping with a backslash is used, then it only makes sense to do this in a 
    file where the backslash is already used as an escape character (in which 
    case we include it). If it is never used as escape for the delimiter or 
    quotechar, then it is not necessary to self-escape.

    """
    no_url = filter_urls(data)
    delims = get_delimiters(no_url, encoding, delimiters=delimiters)
    quotechars = get_quotechars(no_url)
    escapechars = {}

    for delim, quotechar in itertools.product(delims, quotechars):
        escapechars[(delim, quotechar)] = set([""])

    for u, v in pairwise(data):
        if not is_potential_escapechar(u, encoding):
            continue
        for delim, quotechar in itertools.product(delims, quotechars):
            if v == delim or v == quotechar:
                escapechars[(delim, quotechar)].add(u)

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
    if six.PY2:
        as_unicode = codecs.decode(x.encode(encoding), encoding)
    else:
        as_unicode = codecs.decode(bytes(x, encoding), encoding=encoding)
    return unicodedata.category(as_unicode)


def filter_urls(data):
    pat = "(?:(?:[A-Za-z]{3,9}:(?:\/\/)?)(?:[-;:&=\+\$,\w]+@)?[A-Za-z0-9.-]+|(?:www.|[-;:&=\+\$,\w]+@)[A-Za-z0-9.-]+)(?:(?:\/[\+~%\/.\w\-_]*)?\??(?:[-\+=&;%@.\w_]*)#?(?:[\w]*))?"
    return regex.sub(pat, "U", data, count=0)


def get_delimiters(data, encoding, delimiters=None):
    D = set()
    C = [
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
    B = [".", "/", '"', "'", "\n", "\r"]
    for x in set(data):
        c = unicode_category(x, encoding=encoding)
        if delimiters is None:
            if x == "\t" or ((x not in B) and (c not in C)):
                D.add(x)
        else:
            if x in delimiters:
                D.add(x)
    D.add("")
    return D


def get_quotechars(data):
    Q = set(["'", '"', "~", "`"]) & set(data)
    Q.add("")
    return Q


def masked_by_quotechar(data, quotechar, escapechar, test_char):
    """Test if a character is always masked by quote characters

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
