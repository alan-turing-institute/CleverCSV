# -*- coding: utf-8 -*-

"""
Various utilities

Author: Gertjan van den Burg

"""

import chardet


def pairwise(iterable):
    "s - > (s0, s1), (s1, s2), (s2, s3), ..."
    a = iter(iterable)
    b = iter(iterable)
    next(b, None)
    return zip(a, b)


def get_encoding(filename):
    """Get the encoding of the file

    This function uses the chardet package for detecting the encoding of a 
    file.

    Parameters
    ----------
    filename: str
        Path to a file

    Returns
    -------
    encoding: str
        Encoding of the file.
    """
    detector = chardet.UniversalDetector()
    final_chunk = False
    blk_size = 65536
    with open(filename, "rb") as fid:
        while (not final_chunk) and (not detector.done):
            chunk = fid.read(blk_size)
            if len(chunk) < blk_size:
                final_chunk = True
            detector.feed(chunk)
    detector.close()
    encoding = detector.result.get("encoding", None)
    return encoding
