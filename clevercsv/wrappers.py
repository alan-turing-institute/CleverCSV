# -*- coding: utf-8 -*-

"""
Wrappers for some loading/saving functionality.

Author: Gertjan van den Burg

"""

import os
import pandas as pd
import warnings

from pandas.errors import ParserWarning

from .detect import Detector
from .dict_read_write import DictReader
from .exceptions import NoDetectionResult
from .read import reader
from .utils import get_encoding


def read_as_dicts(filename, dialect=None, verbose=False):
    enc = get_encoding(filename)
    with open(filename, "r", newline="", encoding=enc) as fid:
        if dialect is None:
            dialect = Detector().detect(fid.read(), verbose=verbose)
            fid.seek(0)
        r = DictReader(fid, dialect=dialect)
        for row in r:
            yield row


def read_csv(
    filename, dialect=None, encoding=None, num_chars=None, verbose=False
):
    """Read a CSV file as a list of lists

    This is a convenience function that reads a CSV file and returns the data 
    as a list of lists (= rows).

    Parameters
    ----------
    filename: str
        Path of the CSV file

    dialect: str, SimpleDialect, or csv.Dialect object
        If the dialect is known, it can be provided here. This function uses 
        the CleverCSV :class:``reader`` object, which supports various dialect 
        types (string, SimpleDialect, or csv.Dialect). If None, the dialect 
        will be detected.

    encoding : str
        The encoding of the file. If None, it is detected.

    num_chars : int
        Number of characters to use to detect the dialect. If None, use the 
        entire file.

        Note that using less than the entire file will speed up detection, but 
        can reduce the accuracy of the detected dialect.

    verbose: bool
        Whether or not to show detection progress.

    Returns
    -------
    rows: list
        Returns rows as a list of lists.

    Raises
    ------
    NoDetectionResult
        When the dialect detection fails.

    """
    if encoding is None:
        encoding = get_encoding(filename)
    with open(filename, "r", newline="", encoding=encoding) as fid:
        if dialect is None:
            data = fid.read(num_chars) if num_chars else fid.read()
            dialect = Detector().detect(data, verbose=verbose)
            if dialect is None:
                raise NoDetectionResult()
            fid.seek(0)
        r = reader(fid, dialect)
        return list(r)


def csv2df(filename, *args, **kwargs):
    """ Read a CSV file to a Pandas dataframe

    This function uses CleverCSV to detect the dialect, and then passes this to 
    the ``read_csv`` function in pandas. Additional arguments and keyword 
    arguments are passed to ``read_csv`` as well.

    Parameters
    ----------

    filename: str
        The filename of the CSV file. At the moment, only local files are 
        supported.

    *args:
        Additional arguments for the ``pandas.read_csv`` function.

    **kwargs:
        Additional keyword arguments for the ``pandas.read_csv`` function.

    """
    if not (os.path.exists(filename) and os.path.isfile(filename)):
        raise ValueError("Filename must be a regular file")
    enc = get_encoding(filename)
    with open(filename, "r", newline="", encoding=enc) as fid:
        dialect = Detector().detect(fid.read())
    csv_dialect = dialect.to_csv_dialect()

    # This is used to catch pandas' warnings when a dialect is supplied.
    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            message="^Conflicting values for .*",
            category=ParserWarning,
        )
        df = pd.read_csv(filename, *args, dialect=csv_dialect, **kwargs)
    return df


def detect_dialect(filename, num_chars=None, encoding=None, verbose=False):
    """Detect the dialect of a CSV file

    This is a utility function that simply returns the detected dialect of a 
    given CSV file.

    Parameters
    ----------
    filename : str
        The filename of the CSV file.

    num_chars : int
        Number of characters to read for the detection. If None, the entire 
        file will be read. Note that limiting the number of characters can 
        reduce the accuracy of the detected dialect.

    encoding : str
        The file encoding of the CSV file. If None, it is detected.

    verbose : bool
        Enable verbose mode during detection.

    Returns
    -------
    dialect : SimpleDialect
        The detected dialect as a :class:`SimpleDialect`, or None if detection 
        failed.

    """
    enc = encoding or get_encoding(filename)
    with open(filename, "r", newline="", encoding=enc) as fp:
        data = fp.read(num_chars) if num_chars else fp.read()
        dialect = Detector().detect(data, verbose=verbose)
    return dialect
