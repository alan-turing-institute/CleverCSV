#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Wrapper for Python dialect Sniffer.

Author: Gertjan van den Burg

"""

import csv

from utils import DetectionError, get_sample, parse_args


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

if __name__ == "__main__":
    from clevercsv.utils import get_encoding

    args = parse_args()
    encoding = get_encoding(args.filename)
    print(detector(args.filename, encoding, n_lines=args.n))
