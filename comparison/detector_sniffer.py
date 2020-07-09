#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Wrapper for Python dialect Sniffer.

Author: Gertjan van den Burg

"""

import csv

from utils import DetectionError, get_sample


def detector(gz_filename, encoding, n_lines=None):
    sniffer = csv.Sniffer()
    sample = get_sample(gz_filename, encoding, n_lines=n_lines)

    try:
        (
            quotechar,
            doublequote,
            delimiter,
            skipinitialsapce,
        ) = sniffer._guess_quote_and_delimiter(sample, None)
    except csv.Error:
        raise DetectionError

    if not delimiter:
        delimiter, skipinitialspace = sniffer._guess_delimiter(sample, None)
        if not delimiter:
            return None
    dialect = dict(delimiter=delimiter, quotechar=quotechar, escapechar="")
    return dialect
