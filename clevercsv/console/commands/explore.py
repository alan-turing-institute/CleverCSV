# -*- coding: utf-8 -*-

import code
import sys

from wilderness import Command

from clevercsv.encoding import get_encoding
from clevercsv.wrappers import detect_dialect

from ._docs import FLAG_DESCRIPTIONS
from ._utils import generate_code
from ._utils import parse_int


class ExploreCommand(Command):
    _description = (
        "The explore command allows you to quickly explore a CSV file in an "
        "interactive Python shell. This command detects the dialect of the "
        "CSV file and drops you into a Python interactive shell (REPL), "
        "with the CSV file already loaded. Simply run:\n\n"
        "\tclevercsv explore FILE\n\n"
        "to start working with the file loaded as a list of lists. "
        "Alternatively, you can run:\n\n"
        "\tclevercsv explore -p FILE\n\n"
        "to read the file as a Pandas dataframe."
    )

    def __init__(self) -> None:
        super().__init__(
            name="explore",
            title="Explore the CSV file in an interactive Python shell",
            description=self._description,
            extra_sections={"CleverCSV": "Part of the CleverCSV suite"},
        )

    def register(self) -> None:
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
            "-p",
            "--pandas",
            action="store_true",
            help="Read the file into a Pandas DataFrame",
            description=(
                "By default, this command imports the CSV file as a list of "
                "lists. By enabling this option the script will be written "
                "such that the file will be read as a Pandas DataFrame "
                "instead."
            ),
        )

    def handle(self) -> int:
        filename = self.args.path
        encoding = self.args.encoding or get_encoding(filename)
        num_chars = parse_int(self.args.num_chars, "num-chars")
        dialect = detect_dialect(
            filename,
            num_chars=num_chars,
            encoding=encoding,
            verbose=self.args.verbose,
        )
        if dialect is None:
            print("Error: dialect detection failed.", file=sys.stderr)
            return 1

        code_lines = generate_code(
            filename, dialect, encoding, use_pandas=self.args.pandas
        )

        console = code.InteractiveConsole()
        for line in code_lines:
            retcode = console.push(line)
        if retcode:
            print(
                "An error occurred starting the interactive console. "
                "Printing commands instead:\n"
            )
            print("\n".join(code_lines))
            return 1

        print("Dropping you into an interactive shell.\n")
        banner = "CleverCSV has loaded the data into the variable: "
        banner += "df" if self.args.pandas else "rows"
        console.interact(banner=banner)
        return 0
