# -*- coding: utf-8 -*-

"""
Drop-in replacement for Python Sniffer object.

Author: Gertjan van den Burg

"""

from io import StringIO

from .consistency import detect_dialect_consistency
from .normal_form import detect_dialect_normal
from .read import reader


class Detector(object):
    """
    Detect the Dialect of CSV files with normal forms or the data consistency 
    measure. This class provides a drop-in replacement for the Python dialect 
    Sniffer from the standard library.

    Note
    ----
    We call the object ``Detector`` just to mark the difference in the 
    implementation and avoid naming issues. You can import it as ``from ccsv 
    import Sniffer`` nonetheless.

    """

    def __init__(self):
        pass

    def sniff(self, sample, delimiters=None, verbose=False):
        # Compatibility method for Python
        return self.detect(sample, delimiters=delimiters, verbose=verbose)

    def detect(self, sample, delimiters=None, verbose=False):
        if verbose:
            print("Running normal form detection ...")
        dialect = detect_dialect_normal(
            sample, delimiters=delimiters, verbose=verbose
        )
        if not dialect is None:
            self.method_ = "normal"
            return dialect
        self.method_ = "consistency"
        if verbose:
            print("Running data consistency measure ...")
        return detect_dialect_consistency(
            sample, delimiters=delimiters, verbose=verbose
        )

    def has_header(self, sample):
        """Detect if a file has a header from a sample.

        This function is copied from CPython! The only change we've made is to 
        use our dialect detection method.

        """

        # Creates a dictionary of types of data in each column. If any
        # column is of a single type (say, integers), *except* for the first
        # row, then the first row is presumed to be labels. If the type
        # can't be determined, it is assumed to be a string in which case
        # the length of the string is the determining factor: if all of the
        # rows except for the first are the same length, it's a header.
        # Finally, a 'vote' is taken at the end for each column, adding or
        # subtracting from the likelihood of the first row being a header.

        rdr = reader(StringIO(sample), self.sniff(sample))

        header = next(rdr)  # assume first row is header

        columns = len(header)
        columnTypes = {}
        for i in range(columns):
            columnTypes[i] = None

        checked = 0
        for row in rdr:
            # arbitrary number of rows to check, to keep it sane
            if checked > 20:
                break
            checked += 1

            if len(row) != columns:
                continue  # skip rows that have irregular number of columns

            for col in list(columnTypes.keys()):

                for thisType in [int, float, complex]:
                    try:
                        thisType(row[col])
                        break
                    except (ValueError, OverflowError):
                        pass
                else:
                    # fallback to length of string
                    thisType = len(row[col])

                if thisType != columnTypes[col]:
                    if columnTypes[col] is None:  # add new column type
                        columnTypes[col] = thisType
                    else:
                        # type is inconsistent, remove column from
                        # consideration
                        del columnTypes[col]

        # finally, compare results against first row and "vote"
        # on whether it's a header
        hasHeader = 0
        for col, colType in columnTypes.items():
            if type(colType) == type(0):  # it's a length
                if len(header[col]) != colType:
                    hasHeader += 1
                else:
                    hasHeader -= 1
            else:  # attempt typecast
                try:
                    colType(header[col])
                except (ValueError, TypeError):
                    hasHeader += 1
                else:
                    hasHeader -= 1

        return hasHeader > 0
