#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Default dialect: comma delimiter and quotes only if present.

Author: Gertjan van den Burg

"""


from utils import get_sample, parse_args


def detector(gz_filename, encoding, n_lines=None):
    sample = get_sample(gz_filename, encoding, n_lines=n_lines)
    quotechar = ""
    if '",' in sample or ',"' in sample or '","' in sample:
        quotechar = '"'

    return dict(delimiter=",", quotechar=quotechar, escapechar="")


if __name__ == "__main__":
    from clevercsv.utils import get_encoding

    args = parse_args()
    encoding = get_encoding(args.filename)
    print(detector(args.filename, encoding, n_lines=args.n))
