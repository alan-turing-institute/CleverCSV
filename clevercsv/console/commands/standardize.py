# -*- coding: utf-8 -*-

import io
import os
import tempfile
import shutil

from cleo import Command

from clevercsv.read import reader
from clevercsv.utils import get_encoding, sha1sum
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
        { --i|in-place : Standardize and overwrite the input file. }
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
        """Handle the standardize command

        The return value of this method is the exit code of the command, with 0
        meaning success.

        """
        verbose = self.io.verbosity > 0
        path = self.argument("path")
        num_chars = parse_int(self.option("num-chars"), "num-chars")
        self.encoding = self.option("encoding") or get_encoding(path)

        if self.option("in-place") and self.option("output"):
            self.line(
                "Incompatible options '-i/--in-place' and '-o/--output'. "
                "Can't edit file in-place and write to an output file."
            )
            return 1

        dialect = detect_dialect(
            path, num_chars=num_chars, encoding=self.encoding, verbose=verbose
        )
        if dialect is None:
            self.line("Dialect detection failed.")
            return 1

        if self.option("in-place"):
            return self._in_place(dialect)
        elif self.option("output") is None:
            return self._to_stdout(dialect)
        return self._to_file(dialect)

    def _write_transposed(self, stream, dialect):
        path = self.argument("path")
        with open(path, "r", newline="", encoding=self.encoding) as fp:
            read = reader(fp, dialect=dialect)
            rows = list(read)
        rows = list(map(list, zip(*rows)))
        write = writer(stream, dialect="excel")
        for row in rows:
            write.writerow(row)

    def _write_direct(self, stream, dialect):
        path = self.argument("path")
        with open(path, "r", newline="", encoding=self.encoding) as fp:
            read = reader(fp, dialect=dialect)
            write = writer(stream, dialect="excel")
            for row in read:
                write.writerow(row)

    def _write_to_stream(self, stream, dialect):
        if self.option("transpose"):
            self._write_transposed(stream, dialect)
        else:
            self._write_direct(stream, dialect)

    def _in_place(self, dialect):
        """In-place mode overwrites the input file, if necessary

        The return value of this method is to be used as the status code of
        the command. A return value of 0 means no edits were made as the file
        was already in the correct format, and a value of 2 means the file was
        modified.

        """
        tmpfd, tmpfname = tempfile.mkstemp(prefix="clevercsv_", suffix=".csv")
        tmpid = os.fdopen(tmpfd, "w", newline="", encoding=self.encoding)
        self._write_to_stream(tmpid, dialect)
        tmpid.close()

        previous_sha1 = sha1sum(self.argument("path"))
        new_sha1 = sha1sum(tmpfname)
        if previous_sha1 == new_sha1:
            os.unlink(tmpfname)
            return 0

        shutil.move(tmpfname, self.argument("path"))
        return 2

    def _to_stdout(self, dialect):
        stream = io.StringIO(newline="")
        self._write_to_stream(stream, dialect)
        self.overwrite(stream.getvalue())
        stream.close()
        return 0

    def _to_file(self, dialect):
        with open(
            self.option("output"), "w", newline="", encoding=self.encoding
        ) as fp:
            self._write_to_stream(fp, dialect)
        return 0
