# -*- coding: utf-8 -*-

import code

from cleo import Command

from clevercsv.utils import get_encoding
from clevercsv.wrappers import detect_dialect

from ._utils import parse_int, generate_code


class ExploreCommand(Command):
    """
    Drop into a Python shell with the CSV file loaded

    explore
        { path : The path to the CSV file }
        { --e|encoding= : Set the encoding of the CSV file. }
        { --n|num-chars= : Limit the number of characters to read for 
        detection. This will speed up detection for large files, but may reduce 
        accuracy. }
        { --p|pandas : Read file into a Pandas dataframe. }
    """

    help = """\
The <info>explore</info> command allows you to quickly explore a CSV file in an 
interactive Python shell. This command detects the dialect of the CSV file and 
drops you into a Python interactive shell (REPL), with the CSV file already 
loaded. Simply run:

clevercsv explore FILE

to start working with the file loaded as a list of lists. Alternatively, you 
can run

clevercsv explore -p FILE

to read the file as a Pandas dataframe.
"""

    def handle(self):
        filename = self.argument("path")
        encoding = self.option("encoding") or get_encoding(filename)
        num_chars = parse_int(self.option("num-chars"), "num-chars")
        dialect = detect_dialect(
            filename,
            num_chars=num_chars,
            encoding=encoding,
            verbose=self.option("verbose"),
        )
        if dialect is None:
            return self.line("Dialect detection failed.")

        code_lines = generate_code(
            filename, dialect, encoding, use_pandas=self.option("pandas")
        )

        console = code.InteractiveConsole()
        for line in code_lines:
            retcode = console.push(line)
        if retcode:
            self.line(
                "An error occurred starting the interactive console. "
                "Printing commands instead:\n"
            )
            self.line("\n".join(code_lines))
            return
        self.line("Dropping you into an interactive shell.\n")
        banner = "CleverCSV has loaded the data into the variable: "
        banner += "df" if self.option("pandas") else "rows"
        console.interact(banner=banner)
