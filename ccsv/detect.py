# -*- coding: utf-8 -*-

"""
Drop-in replacement for Python Sniffer object

Author: Gertjan van den Burg

"""

from .normal_form import detect_dialect_normal
from .consistency import detect_dialect_consistency


class Detector(object):
    """
    Detect the Dialect of CSV files with normal forms or the data consistency 
    measure. This class provides a drop-in replacement for the Python dialect 
    Sniffer from the stdlib.
    """

    def __init__(self):
        pass

    def sniff(self, sample, delimiters=None):
        # Compatibility method for Python
        return self.detect(sample, delimiters)

    def detect(self, sample, delimiters=None):
        dialect = detect_dialect_normal(sample, delimiters=delimiters)
        if not dialect is None:
            self.method_ = 'normal'
            return dialect
        self.method_ = 'consistency'
        return detect_dialect_consistency(sample, delimiters=delimiters)

    def has_header(self, sample):
        raise NotImplementedError
