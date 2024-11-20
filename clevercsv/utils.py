# -*- coding: utf-8 -*-

"""
Various utilities

Author: Gertjan van den Burg

"""

from __future__ import annotations

import hashlib

from typing import TYPE_CHECKING
from typing import Iterable
from typing import Iterator
from typing import Optional
from typing import Tuple
from typing import TypeVar

from clevercsv._types import AnyPath

T = TypeVar("T")


if TYPE_CHECKING:
    import logging


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


def maybe_log_or_print(
    msg: str, verbose: bool = False, logger: Optional[logging.Logger] = None
) -> None:
    """Log or print a message if verbose is True

    Parameters
    ----------
    msg : str
        The message to log or print.
    verbose : bool
        Whether to log or print a message.
    logger : Optional[logging.Logger]
        A logger instance.
    """
    if verbose:
        if logger is not None:
            logger.info(msg)
        else:
            print(msg)
