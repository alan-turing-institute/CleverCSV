# -*- coding: utf-8 -*-

from .__version__ import __version__

from csv import QUOTE_ALL, QUOTE_MINIMAL, QUOTE_NONNUMERIC, QUOTE_NONE

from .cparser_util import field_size_limit
from .detect import Detector
from .detect import Detector as Sniffer
from .dict_read_write import DictReader, DictWriter
from .exceptions import Error
from .read import reader
from .wrappers import (
    detect_dialect,
    read_dataframe,
    read_dicts,
    read_table,
    stream_dicts,
    stream_table,
    write_table,
)
from .write import writer

# outdated, to be removed in 0.7.0
from .wrappers import read_as_dicts, read_csv, stream_csv, csv2df
