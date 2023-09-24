# -*- coding: utf-8 -*-

import sys

from wilderness import Command

from clevercsv.encoding import get_encoding
from clevercsv.wrappers import detect_dialect

from ._docs import FLAG_DESCRIPTIONS
from ._utils import generate_code
from ._utils import parse_int


class CodeCommand(Command):
    _description = (
        "Generate Python code for importing a given CSV file. This is "
        "especially useful if you don't want to repeatedly detect the dialect "
        "of the same file. Simply run:\n\n"
        "\tclevercsv code your_csv_file.csv\n\n"
        "and copy the generated code to a Python script."
    )

    def __init__(self) -> None:
        super().__init__(
            name="code",
            title="Generate Python code to import a CSV file",
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
            type=int,
            help="Number of characters to use for detection",
            description=FLAG_DESCRIPTIONS["num-chars"],
        )
        self.add_argument(
            "-p",
            "--pandas",
            action="store_true",
            help="Write code that uses a Pandas DataFrame",
            description=(
                "By default, this command writes a small Python script to "
                "import the CSV file as a list of lists. By enabling this "
                "option the script will be written such that the file will be "
                "read as a Pandas DataFrame instead."
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
        print("\n".join(code_lines))
        return 0
