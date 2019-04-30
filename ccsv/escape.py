# -*- coding: utf-8 -*-

"""
Common functions for dealing with escape characters.

Author: Gertjan van den Burg
Date: 2018-11-06
"""

import codecs
import six
import unicodedata


def is_potential_escapechar(char, encoding):
    if six.PY2:
        as_unicode = codecs.decode(char.encode(encoding), encoding)
    else:
        as_unicode = codecs.decode(bytes(char, encoding), encoding=encoding)
    ctr = unicodedata.category(as_unicode)
    block = ["!", "?", '"', "'", ".", ",", ";", ":", "%", "*", "&", "#"]
    if ctr == "Po":
        if as_unicode in block:
            return False
        return True
    return False
