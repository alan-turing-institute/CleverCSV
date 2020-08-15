#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Detector that iteratively "grows" the buffer that CleverCSV uses.

Suggested by https://github.com/jlumbroso

"""

import clevercsv

from utils import DetectionError, get_sample, count_lines, parse_args


def trailing_equality(l, k=4):
    # Ensure that the last k elements of the list l are equal
    if len(l) < k:
        return False
    return len(set(l[-k:])) == 1


def detect_dialect(filename, encoding, n_lines):
    det = clevercsv.Detector()
    sample = get_sample(filename, encoding, n_lines=n_lines)
    try:
        dialect = det.detect(sample)
    except clevercsv.Error:
        raise DetectionError

    if dialect is None:
        return None
    return dialect


def detector(filename, encoding, n_lines=None, lines_start=100, n_equal=5):
    # Note: n_lines here is the *maximum* number of lines to read. If it is
    # None, in theory the entire file can be read.

    # This function is based on jlumbroso's Gist:
    # https://gist.github.com/jlumbroso/c123a30a2380b58989c7b12fe4b4f49e

    # The hope is that for large files, this is faster than reading the entire
    # file yet doesn't lose significantly in accuracy (which is what we want to
    # test!)

    have_lines = count_lines(filename, encoding)
    if n_lines is None:
        max_lines = have_lines
    else:
        max_lines = min(n_lines, have_lines)

    dialects = []
    current_lines = lines_start
    if current_lines >= max_lines:
        dialects.append(detect_dialect(filename, encoding, max_lines))

    while (
        not trailing_equality(dialects, n_equal) and current_lines < max_lines
    ):
        dialects.append(detect_dialect(filename, encoding, current_lines))
        current_lines *= 2

    dialect = dialects[-1]
    if dialect is None:
        return dialect
    return dict(
        delimiter=dialect.delimiter,
        quotechar=dialect.quotechar,
        escapechar=dialect.escapechar,
    )


if __name__ == "__main__":
    args = parse_args()
    encoding = clevercsv.utils.get_encoding(args.filename)
    print(detector(args.filename, encoding, n_lines=args.n))
