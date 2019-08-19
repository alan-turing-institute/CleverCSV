# -*- coding: utf-8 -*-

import ast
import io
import textwrap

from cleo import Command

from clevercsv import __version__
from clevercsv import Detector, reader
from clevercsv.potential_dialects import filter_urls, get_delimiters
from clevercsv.utils import get_encoding
from clevercsv.wrappers import detect_dialect

from .._flags import INTERACT_NONE, INTERACT_NECESSARY
from ._utils import parse_int
from ._warnings import WARNINGS


class CodeGenCommand(Command):
    """
    Generate Python code for importing the CSV file

    codegen
        { path : The path to the CSV file }
        { --e|encoding= : Set the encoding of the CSV file. }
        { --n|num-chars= : Limit the number of characters to read for
        detection. This will speed up detection but may reduce accuracy. }
        { --p|pandas : Write code that imports to a Pandas DataFrame }
    """

    help = """\
The <info>codegen</info> command generates Python code for importing the 
specified CSV file. This is especially useful if you don't want to repeatedly 
detect the dialect of the same file. Simply run:

clevercsv codegen yourfile.csv

and copy the generated code to a Python script.
"""

    def handle(self):
        self.filename = self.argument("path")
        self.encoding = self.option("encoding") or get_encoding(self.filename)
        self.num_chars = parse_int(self.option("num-chars"), "num-chars")
        self.verbose = self.option("verbose")

        if self.interactive == INTERACT_NONE:
            self.handle_noninteractive()
        else:
            self.handle_interactive()

    @property
    def interactive(self):
        return self._io._interactivity

    def handle_noninteractive(self):
        dialect = detect_dialect(
            self.filename,
            num_chars=self.num_chars,
            encoding=self.encoding,
            verbose=self.verbose,
        )
        if dialect is None:
            return self.line_error(
                "\n<error>"
                + textwrap.fill(
                    "Dialect detection failed. You can use interactive mode "
                    "(-i) to help the detection succeed!"
                )
                + "</error>"
            )
        self.print_result(dialect)

    def handle_interactive(self):
        with open(
            self.filename, "r", newline="", encoding=self.encoding
        ) as fp:
            try:
                data = fp.read()
            except UnicodeDecodeError:
                return self.line(WARNINGS["unicodedecodeerror"])
        no_url = filter_urls(data)

        delimiters = None
        while True:
            delimiters = get_delimiters(
                no_url, self.encoding, delimiters=delimiters
            )
            dialect = Detector().detect(
                data, delimiters=delimiters, verbose=self.verbose
            )
            # With INTERACT_NECESSARY we only interact if dialect is not None
            if not dialect is None and self.interactive == INTERACT_NECESSARY:
                return self.print_result(dialect)

            if not dialect is None:
                self.show_preview(data, dialect)
                if self.ask_okay():
                    return self.print_result(dialect)
            delimiters = self.ask_delimiters(delimiters)

    def show_preview(self, data, dialect, n_rows=5, n_cols=5):
        self.line("\n<info>The detected dialect is:</info>")
        self.line(f"\tdelimiter = {repr(dialect.delimiter)}".strip())
        self.line(f"\tquotechar = {repr(dialect.quotechar)}".strip())
        self.line(f"\tescapechar = {repr(dialect.escapechar)}".strip())
        self.line("")
        self.line(
            "<info>"
            + textwrap.fill(
                "Here is a preview of the first few lines and columns of the "
                "parsed file using the detected dialect:"
            )
            + "</info>"
        )

        table = []
        r = reader(io.StringIO(data, newline=""), dialect=dialect)
        for row in r:
            table.append(row[:n_cols])
            if len(table) == n_rows:
                break
        max_len = max(map(len, table))
        padded = [r + [""] * (max_len - len(r)) for r in table]
        table = self.table()
        for row in padded:
            table.add_row(row)
        table.render(self.io)
        self.line("")

    def ask_okay(self):
        return self.confirm("Do you want to continue with this dialect?", True)

    def ask_delimiters(self, delimiters):
        delimiters = self.choice(
            "Please select the potential delimiters that you want to allow "
            "(numbers separated by comma)",
            sorted(map(repr, delimiters)),
            multiple=True,
        )
        clean_delim = [ast.literal_eval(d) for d in delimiters]
        return clean_delim

    def print_result(self, dialect):
        self.line("\n<info>Here is the generated Python code:</info>\n")
        d = repr(f"{dialect.delimiter}").replace("'", '"')
        q = '"%s"' % (dialect.quotechar.replace('"', '\\"'))
        e = repr(f"{dialect.escapechar}").replace("'", '"')
        base = [
            "",
            f"# Code generated with CleverCSV version {__version__}",
            "",
            "import clevercsv",
        ]
        if self.option("pandas"):
            code = base + [
                "",
                f'df = clevercsv.csv2df("{self.filename}", delimiter={d}, '
                "quotechar={q}, escapechar={e})",
                "",
            ]
        else:
            enc = "None" if self.encoding is None else f'"{self.encoding}"'
            code = base + [
                "",
                f'with open("{self.filename}", "r", newline="", encoding={enc}) as fp:',
                f"    reader = clevercsv.reader(fp, "
                + f"delimiter={d}, quotechar={q}, escapechar={e})",
                "    rows = list(reader)",
                "",
            ]
        self.line("\n".join(code))
