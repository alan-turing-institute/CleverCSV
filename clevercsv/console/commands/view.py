# -*- coding: utf-8 -*-

import sys

try:
    import tabview
except ImportError:

    class TabView:
        def view(*args, **kwargs):
            print(
                "Error: unfortunately Tabview is not available on Windows.",
                file=sys.stderr,
            )

    tabview = TabView()


from wilderness import Command

from clevercsv.exceptions import NoDetectionResult
from clevercsv.wrappers import read_table

from ._docs import FLAG_DESCRIPTIONS
from ._utils import parse_int


class ViewCommand(Command):

    _description = (
        "The view command is useful to quickly inspect a messy CSV file on "
        "the command line."
    )

    def __init__(self):
        super().__init__(
            name="view",
            title="View the CSV file on the command line using TabView",
            description=self._description,
            extra_sections={"CleverCSV": "Part of the CleverCSV suite"},
        )

    def register(self):
        self.add_argument("path", help="Path to the CSV file")
        self.add_argument(
            "-e",
            "--encoding",
            help="Set the encoding of the file",
            description=FLAG_DESCRIPTIONS["encoding"],
        )
        self.add_argument(
            "-n",
            "--num-chars",
            help="Number of characters to use for detection",
            type=int,
            description=FLAG_DESCRIPTIONS["num-chars"],
        )
        self.add_argument(
            "-t",
            "--transpose",
            action="store_true",
            help="Transpose the columns of the input file before viewing",
        )

    def handle(self) -> int:
        verbose = self.args.verbose
        num_chars = parse_int(self.args.num_chars, "num-chars")
        try:
            rows = read_table(
                self.args.path,
                encoding=self.args.encoding,
                num_chars=num_chars,
                verbose=verbose,
            )
        except NoDetectionResult:
            print("Error: dialect detection failed.", file=sys.stderr)
            return 1

        if self.args.transpose:
            max_row_length = max(map(len, rows))
            fixed_rows = []
            for row in rows:
                if len(row) == max_row_length:
                    fixed_rows.append(row)
                else:
                    fixed_rows.append(
                        row + [None] * (max_row_length - len(row))
                    )
            rows = list(map(list, zip(*fixed_rows)))
        tabview.view(rows)
        return 0
