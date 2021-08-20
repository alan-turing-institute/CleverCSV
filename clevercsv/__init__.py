# -*- coding: utf-8 -*-

from csv import QUOTE_ALL
from csv import QUOTE_MINIMAL
from csv import QUOTE_NONE
from csv import QUOTE_NONNUMERIC

from .__version__ import __version__
from .cparser_util import field_size_limit
from .detect import Detector
from .detect import Detector as Sniffer
from .dict_read_write import DictReader
from .dict_read_write import DictWriter
from .exceptions import Error
from .read import reader
from .wrappers import detect_dialect
from .wrappers import read_dataframe
from .wrappers import read_dicts
from .wrappers import read_table
from .wrappers import stream_dicts
from .wrappers import stream_table
from .wrappers import write_table
from .write import writer
