# -*- coding: utf-8 -*-

"""
Definitions for the ``detect`` command of the CleverCSV CLI.
"""

from cleo import Command

from clevercsv.utils import get_encoding
from clevercsv.wrappers import detect_dialect

from ._utils import parse_int
from ._warnings import WARNINGS


class DetectCommand(Command):
    """
    Detect the dialect of a CSV file

    detect
        { path : The path to the CSV file }
        { --e|encoding= : Set the encoding of the CSV file }
        { --n|num-chars= : Limit the number of characters to read for
        detection. This will speed up detection but may reduce accuracy. }
        { --p|plain : Print the components of the dialect on separate lines. }
    """

    help = "The <info>detect</info> command detects the dialect of a given CSV file."

    def handle(self):
        self.filename = self.argument("path")
        self.encoding = self.option("encoding") or get_encoding(self.filename)
        verbose = self.io.verbosity > 0
        num_chars = parse_int(self.option("num-chars"), "num-chars")
        try:
            dialect = detect_dialect(
                self.filename,
                num_chars=num_chars,
                encoding=self.encoding,
                verbose=verbose,
            )
        except UnicodeDecodeError:
            return self.line_error(WARNINGS["unicodedecodeerror"])

        if dialect is None:
            return self.line("Dialect detection failed.")

        if self.option("plain"):
            self.line(f"delimiter = {dialect.delimiter}".strip())
            self.line(f"quotechar = {dialect.quotechar}".strip())
            self.line(f"escapechar = {dialect.escapechar}".strip())
        else:
            self.line("Detected: " + str(dialect))
