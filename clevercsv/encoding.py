# -*- coding: utf-8 -*-

"""Functionality to detect file encodings

Author: G.J.J. van den Burg
License: See the LICENSE file

This file is part of CleverCSV.

"""

from typing import Optional

import chardet

from ._optional import import_optional_dependency
from ._types import _OpenFile


def get_encoding(
    filename: _OpenFile, try_cchardet: bool = True
) -> Optional[str]:
    """Get the encoding of the file

    This function uses the chardet package for detecting the encoding of a
    file.

    Parameters
    ----------
    filename: str
        Path to a file

    try_cchardet: bool
        Whether to run detection using cChardet if it is available. This can be
        faster, but may give different results than using chardet.

    Returns
    -------
    encoding: str
        Encoding of the file.
    """
    if try_cchardet:
        cchardet = import_optional_dependency(
            "cchardet", raise_on_missing=False
        )
    else:
        cchardet = None

    if cchardet is None:
        detector = chardet.UniversalDetector()
    else:
        detector = cchardet.UniversalDetector()

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
