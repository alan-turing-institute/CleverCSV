# -*- coding: utf-8 -*-

"""
Wrappers for easy loading of data from files.

Author: Gertjan van den Burg

"""


import pandas as pd

from .detect import Detector
from .dict_read_write import DictReader
from .utils import get_encoding
from .read import reader


def read_as_dataframe(filename, dialect=None, verbose=False):
    enc = get_encoding(filename)
    with open(filename, "r", newline="", encoding=enc) as fid:
        if dialect is None:
            dialect = Detector().detect(fid.read(), verbose=verbose)
            fid.seek(0)
        r = reader(fid, dialect)
        rows = list(r)
    return pd.DataFrame.from_records(rows)



def read_as_dicts(filename, dialect=None, verbose=False):
    enc = get_encoding(filename)
    with open(filename, "r", newline="", encoding=enc) as fid:
        if dialect is None:
            dialect = Detector().detect(fid.read(), verbose=verbose)
            fid.seek(0)
        r = DictReader(fid, dialect=dialect)
        for row in r:
            yield row
