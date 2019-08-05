# -*- coding: utf-8 -*-

"""
Exceptions for CleverCSV

Author: Gertjan van den Burg

"""

from .cparser import Error as ParserError


class Error(ParserError):
    pass


class NoDetectionResult(Exception):
    pass
