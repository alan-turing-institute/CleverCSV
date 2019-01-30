# -*- coding: utf-8 -*-

"""
Common functions for dealing with escape characters.

Author: Gertjan van den Burg
Date: 2018-11-06
"""

import codecs
import unicodedata


def is_potential_escapechar(char, encoding):
    as_unicode = codecs.decode(bytes(char, encoding), encoding=encoding)
    ctr = unicodedata.category(as_unicode)
    block = ["!", "?", '"', "'", ".", ",", ";", ":", "%", "*", "&", "#"]
    if ctr == "Po":
        if as_unicode in block:
            return False
        return True
    return False
