# -*- coding: utf-8 -*-

from cleo import Command

from clevercsv.encoding import get_encoding
from clevercsv.wrappers import detect_dialect

from ._utils import parse_int, generate_code


class CodeCommand(Command):
    """
    Generate Python code for importing the CSV file

    code
        { path : The path to the CSV file }
        { --e|encoding= : Set the encoding of the CSV file. }
        { --i|interact : Drop into a Python interactive shell. }
        { --n|num-chars= : Limit the number of characters to read for
        detection. This will speed up detection but may reduce accuracy. }
        { --p|pandas : Write code that imports to a Pandas DataFrame }
    """

    help = """\
The <info>code</info> command generates Python code for importing the specified 
CSV file. This is especially useful if you don't want to repeatedly detect the 
dialect of the same file. Simply run:

clevercsv code yourfile.csv

and copy the generated code to a Python script.
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

        self.line("\n".join(code_lines))
