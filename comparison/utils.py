#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Utilities.

Author: Gertjan van den Burg
"""

import argparse
import chardet
import gzip


class DetectionError(Exception):
    pass


def get_sample(filename, encoding, n_lines=None):
    if filename.endswith(".gz"):
        fp = gzip.open(filename, "rt", newline="", encoding=encoding)
    else:
        fp = open(filename, "r", newline="", encoding=encoding)

    if n_lines is None:
        sample = fp.read()
    else:
        lines = []
        for line in fp:
            lines.append(line)
            if len(lines) == n_lines:
                break
        sample = "".join(lines)

    fp.close()
    return sample


def get_encoding(filename):
    opener = gzip.open if filename.endswith(".gz") else open
    detector = chardet.UniversalDetector()
    blk_size = 65536
    final_chunk = False
    with opener(filename, "rb") as fp:
        while (not final_chunk) and (not detector.done):
            chunk = fp.read(blk_size)
            if len(chunk) < blk_size:
                final_chunk = True
            detector.feed(chunk)
    detector.close()
    enc = detector.result["encoding"]
    return enc


def count_lines(filename, encoding):
    if filename.endswith(".gz"):
        fp = gzip.open(filename, "rt", newline="", encoding=encoding)
    else:
        fp = open(filename, "r", newline="", encoding=encoding)

    n_lines = 0
    for line in fp:
        n_lines += 1

    fp.close()
    return n_lines


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-n",
        help="Number of lines to use for detection",
        default=None,
        type=int,
    )
    parser.add_argument(
        "filename", help="File to detect dialect for (.csv or .csv.gz)"
    )
    return parser.parse_args()
