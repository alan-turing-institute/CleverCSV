#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Default dialect: comma delimiter and quotes only if present.

Author: Gertjan van den Burg

"""

from utils import get_sample


def detector(gz_filename, encoding, n_lines=None):
    sample = get_sample(gz_filename, encoding, n_lines=n_lines)
    quotechar = ""
    if '",' in sample or ',"' in sample or '","' in sample:
        quotechar = '"'

    return dict(delimiter=",", quotechar=quotechar, escapechar="")
