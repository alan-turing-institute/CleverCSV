# -*- coding: utf-8 -*-

import tabview

from cleo import Command

from clevercsv.exceptions import NoDetectionResult
from clevercsv.wrappers import read_csv

from ._utils import parse_int


class ViewCommand(Command):
    """
    View the CSV file on the command line using TabView

    view
        { path : The path to the CSV file }
        { --e|encoding= : Set the encoding of the CSV file }
        { --n|num-chars= : Limit the number of characters to read for 
        detection. This will speed up detection but may reduce accuracy. }
        { --t|transpose : Transpose the columns of the file before viewing. }
    """

    help = """\
Use the <info>view</info> command to view a CSV file on the command line.
    """

    def handle(self):
        verbose = self.io.verbosity > 0
        num_chars = parse_int(self.option("num-chars"), "num-chars")
        try:
            rows = read_csv(
                self.argument("path"),
                encoding=self.option("encoding"),
                num_chars=num_chars,
                verbose=verbose,
            )
        except NoDetectionResult:
            self.line("Dialect detection failed.")
        if self.option("transpose"):
            rows = list(map(list, zip(*rows)))
        tabview.view(rows)
