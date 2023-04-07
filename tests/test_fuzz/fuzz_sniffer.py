# -*- coding: utf-8 -*-

"""
Script to run PythonFuzz to detect unhandled exceptions in the Sniffer

This file is part of CleverCSV.

"""

from pythonfuzz.main import PythonFuzz

import clevercsv


@PythonFuzz
def fuzz(buf):
    try:
        string = buf.decode("utf-8")
        _ = clevercsv.Sniffer().sniff(string)
    except UnicodeDecodeError:
        pass
    except clevercsv.exceptions.Error:
        pass


if __name__ == "__main__":
    fuzz()
