# -*- coding: utf-8 -*-

"""
Wrappers for some loading/saving functionality.

Author: Gertjan van den Burg

"""

import os
import warnings

from ._optional import import_optional_dependency
from .detect import Detector
from .dict_read_write import DictReader
from .encoding import get_encoding
from .exceptions import NoDetectionResult
from .read import reader
from .write import writer


def stream_dicts(
    filename, dialect=None, encoding=None, num_chars=None, verbose=False
):
    """Read a CSV file as a generator over dictionaries

    This function streams the rows of the CSV file as dictionaries. The keys of
    the dictionaries are assumed to be in the first row of the CSV file. The
    dialect will be detected automatically, unless it is provided.

    Parameters
    ----------
    filename : str
        Path of the CSV file

    dialect : str, SimpleDialect, or csv.Dialect object
        If the dialect is known, it can be provided here. This function uses
        the Clevercsv :class:`clevercsv.DictReader` object, which supports
        various dialect types (string, SimpleDialect, or csv.Dialect). If None,
        the dialect will be detected.

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
    rows: generator
        Returns file as a generator over rows as dictionaries.

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
            fid.seek(0)
        r = DictReader(fid, dialect=dialect)
        for row in r:
            yield row


def read_dicts(
    filename, dialect=None, encoding=None, num_chars=None, verbose=False
):
    """Read a CSV file as a list of dictionaries

    This function returns the rows of the CSV file as a list of dictionaries.
    The keys of the dictionaries are assumed to be in the first row of the CSV
    file. The dialect will be detected automatically, unless it is provided.

    Parameters
    ----------
    filename : str
        Path of the CSV file

    dialect : str, SimpleDialect, or csv.Dialect object
        If the dialect is known, it can be provided here. This function uses
        the Clevercsv :class:`clevercsv.DictReader` object, which supports
        various dialect types (string, SimpleDialect, or csv.Dialect). If None,
        the dialect will be detected.

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
        Returns rows of the file as a list of dictionaries.

    Raises
    ------
    NoDetectionResult
        When the dialect detection fails.

    """
    return list(
        stream_dicts(
            filename,
            dialect=dialect,
            encoding=encoding,
            num_chars=num_chars,
            verbose=verbose,
        )
    )


def read_table(
    filename,
    dialect=None,
    encoding=None,
    num_chars=None,
    verbose=False,
):
    """Read a CSV file as a table (a list of lists)

    This is a convenience function that reads a CSV file and returns the data
    as a list of lists (= rows). The dialect will be detected automatically,
    unless it is provided.

    Parameters
    ----------
    filename: str
        Path of the CSV file

    dialect: str, SimpleDialect, or csv.Dialect object
        If the dialect is known, it can be provided here. This function uses
        the CleverCSV :class:`clevercsv.reader` object, which supports various
        dialect types (string, SimpleDialect, or csv.Dialect). If None, the
        dialect will be detected.

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
    return list(
        stream_table(
            filename,
            dialect=dialect,
            encoding=encoding,
            num_chars=num_chars,
            verbose=verbose,
        )
    )


def stream_table(
    filename,
    dialect=None,
    encoding=None,
    num_chars=None,
    verbose=False,
):
    """Read a CSV file as a generator over rows of a table

    This is a convenience function that reads a CSV file and returns the data
    as a generator of rows. The dialect will be detected automatically, unless
    it is provided.

    Parameters
    ----------
    filename: str
        Path of the CSV file

    dialect: str, SimpleDialect, or csv.Dialect object
        If the dialect is known, it can be provided here. This function uses
        the CleverCSV :class:`clevercsv.reader` object, which supports various
        dialect types (string, SimpleDialect, or csv.Dialect). If None, the
        dialect will be detected.

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
    rows: generator
        Returns file as a generator over rows.

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
        yield from r


def read_dataframe(filename, *args, num_chars=None, **kwargs):
    """Read a CSV file to a Pandas dataframe

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

    num_chars: int
        Number of characters to use for dialect detection. If None, use the
        entire file.

        Note that using less than the entire file will speed up detection, but
        can reduce the accuracy of the detected dialect.

    **kwargs:
        Additional keyword arguments for the ``pandas.read_csv`` function. You
        can specify the file encoding here if needed, and it will be used
        during dialect detection.

    """
    if not (os.path.exists(filename) and os.path.isfile(filename)):
        raise ValueError("Filename must be a regular file")
    pd = import_optional_dependency("pandas")

    # Use provided encoding or detect it, and record it for pandas
    enc = kwargs.get("encoding") or get_encoding(filename)
    kwargs["encoding"] = enc

    with open(filename, "r", newline="", encoding=enc) as fid:
        data = fid.read(num_chars) if num_chars else fid.read()
        dialect = Detector().detect(data)
    csv_dialect = dialect.to_csv_dialect()

    # This is used to catch pandas' warnings when a dialect is supplied.
    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            message="^Conflicting values for .*",
            category=pd.errors.ParserWarning,
        )
        df = pd.read_csv(filename, *args, dialect=csv_dialect, **kwargs)
    return df


def detect_dialect(
    filename,
    num_chars=None,
    encoding=None,
    verbose=False,
    method="auto",
    skip=True,
):
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

    method : str
        Dialect detection method to use. Either 'normal' for normal form
        detection, 'consistency' for the consistency measure, or 'auto' for
        first normal and then consistency.

    skip : bool
        Skip computation of the type score for dialects with a low pattern
        score.

    Returns
    -------
    dialect : SimpleDialect
        The detected dialect as a :class:`SimpleDialect`, or None if detection
        failed.

    """
    enc = encoding or get_encoding(filename)
    with open(filename, "r", newline="", encoding=enc) as fp:
        data = fp.read(num_chars) if num_chars else fp.read()
        dialect = Detector().detect(
            data, verbose=verbose, method=method, skip=skip
        )
    return dialect


def write_table(
    table, filename, dialect="excel", transpose=False, encoding=None
):
    """Write a table (a list of lists) to a file

    This is a convenience function for writing a table to a CSV file.

    Parameters
    ----------
    table : list
        A table as a list of lists. The table must have the same number of
        cells in each row (taking the :attr:`transpose` flag into account).

    filename : str
        The filename of the CSV file to write the table to.

    dialect : SimpleDialect or csv.Dialect
        The dialect to use. The default is the 'excel' dialect, which
        corresponds to RFC4180. This is done to encourage more standardized CSV
        files.

    transpose : bool
        Transpose the table before writing.

    encoding : str
        Encoding to use to write the data to the file. Note that the default
        encoding is platform dependent, which ensures compatibility with the
        Python open() function. It thus defaults to
        `locale.getpreferredencoding()`.

    Raises
    ------
    ValueError:
            When the length of the rows is not constant.

    """

    if transpose:
        table = list(map(list, zip(*table)))

    if len(set(map(len, table))) > 1:
        raise ValueError("Table doesn't have constant row length.")

    with open(filename, "w", newline="", encoding=encoding) as fp:
        w = writer(fp, dialect=dialect)
        w.writerows(table)
