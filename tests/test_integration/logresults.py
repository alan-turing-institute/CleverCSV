#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Nose Plugin to log succes/fail/error to separate files.

The idea is to track these output files in git, so we can tell when we've 
broken a previously successful test case, or fixed a previously broken one.

Author: Gertjan van den Burg
Date: 2019-02-06
"""

import re
import os

from nose.plugins import Plugin

TEST_ID = re.compile(r"^(.*?)(\(.*\))$")


def id_split(idval):
    # from XUnit plugin
    m = TEST_ID.match(idval)
    if m:
        name, fargs = m.groups()
        head, tail = name.rsplit(".", 1)
        return [head, tail + fargs]
    else:
        return idval.rsplit(".", 1)

def get_hash_from_test(test):
    name = id_split(test.id())[-1]
    if not name.startswith('test_dialect'):
        return None
    return name.split('_')[-1]


class LogResults(Plugin):
    def __init__(self, success_file, error_file, failed_file, *args, **kwargs):
        self._success_file = success_file
        self._error_file = error_file
        self._failed_file = failed_file
        super().__init__(*args, **kwargs)
        self.clear_output_files()

    def clear_output_files(self):
        if os.path.exists(self._success_file):
            os.unlink(self._success_file)
        if os.path.exists(self._error_file):
            os.unlink(self._error_file)
        if os.path.exists(self._failed_file):
            os.unlink(self._failed_file)

    def _log(self, logfile, test):
        name = get_hash_from_test(test)
        if not name is None:
            with open(logfile, 'a') as fid:
                fid.write(name + '\n')

    def addSuccess(self, test):
        self._log(self._success_file, test)

    def addError(self, test, err, capt=None):
        self._log(self._error_file, test)

    def addFailure(self, test, err, capt=None, tb_info=None):
        self._log(self._failed_file, test)
