# -*- coding: utf-8 -*-

import io

from cleo import Command

from clevercsv.read import reader
from clevercsv.wrappers import detect_dialect
from clevercsv.write import writer

from ._utils import parse_int


class StandardizeCommand(Command):
    """
    Convert a CSV file to one that conforms to RFC-4180

    standardize
        { path : The path to the CSV file }
        { --e|encoding= : Set the encoding of the CSV file. This will also be
        used for the output file. }
        { --n|num-chars= : Limit the number of characters to read for
        detection. This will speed up detection but may reduce accuracy. }
        { --o|output= : Output file to write to. If omitted, print to stdout.}
        { --t|transpose : Transpose the columns of the file before writing. }
    """

    help = """\
The <info>standardize</info> command can be used to convert a non-standard CSV 
file to the standard RFC-4180 format [1].

[1]: https://tools.ietf.org/html/rfc4180
    """

    def handle(self):
        verbose = self.io.verbosity > 0
        path = self.argument("path")
        output = self.option("output")
        encoding = self.option("encoding")
        num_chars = parse_int(self.option("num-chars"), "num-chars")

        dialect = detect_dialect(
            path, num_chars=num_chars, encoding=encoding, verbose=verbose
        )
        if dialect is None:
            return self.line("Dialect detection failed.")
        out = (
            io.StringIO(newline=None)
            if output is None
            else open(output, "w", encoding=encoding)
        )
        if self.option("transpose"):
            with open(path, "r", newline="", encoding=encoding) as fp:
                read = reader(fp, dialect=dialect)
                rows = list(read)
            rows = list(map(list, zip(*rows)))
            write = writer(out, dialect="excel")
            for row in rows:
                write.writerow(row)
        else:
            with open(path, "r", newline="", encoding=encoding) as fp:
                read = reader(fp, dialect=dialect)
                write = writer(out, dialect="excel")
                for row in read:
                    write.writerow(row)
        if output is None:
            self.overwrite(out.getvalue())
        out.close()
