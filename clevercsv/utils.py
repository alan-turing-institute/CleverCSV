# -*- coding: utf-8 -*-

"""
Various utilities

Author: Gertjan van den Burg

"""

import hashlib

from typing import Iterable
from typing import Iterator
from typing import Tuple
from typing import TypeVar

from clevercsv._types import AnyPath

T = TypeVar("T")


def pairwise(iterable: Iterable[T]) -> Iterator[Tuple[T, T]]:
    "s - > (s0, s1), (s1, s2), (s2, s3), ..."
    a = iter(iterable)
    b = iter(iterable)
    next(b, None)
    return zip(a, b)


def sha1sum(filename: AnyPath) -> str:
    """Compute the SHA1 checksum of a given file

    Parameters
    ----------
    filename : str
        Path to a file

    Returns
    -------
    checksum : str
        The SHA1 checksum of the file contents.
    """
    blocksize = 1 << 16
    hasher = hashlib.sha1()
    with open(filename, "rb") as fp:
        buf = fp.read(blocksize)
        while len(buf) > 0:
            hasher.update(buf)
            buf = fp.read(blocksize)
    return hasher.hexdigest()
