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
        { path* : One or more CSV files to standardize }
        { --e|encoding=* : Set the encoding of the CSV file. This will also be
        used for the output file. When multiple input files are provided but
        only a single encoding is given, the encoding will be used for all
        files. If the encoding is not provided it will be detected. }
        { --i|in-place : Standardize and overwrite the input file(s). }
        { --n|num-chars= : Limit the number of characters to read for
        dialect detection. This will speed up detection but may reduce
        accuracy. }
        { --o|output=* : Output file to write to. If omitted, print to stdout.}
        { --t|transpose : Transpose the columns of the file before writing. }
    """

    help = """\
The <info>standardize</info> command can be used to convert a non-standard CSV 
file to the standard RFC-4180 format [1].

[1]: https://tools.ietf.org/html/rfc4180

When using the --in-place option, the return code of CleverCSV can be used
to check whether a file was altered or not. The return code will be 2 when the 
file was altered and 0 otherwise.
    """

    def handle(self):
        """Handle the standardize command

        The return value of this method is the exit code of the command, with 0
        meaning success.

        """
        verbose = self.io.verbosity > 0
        paths = self.argument("path")
        outputs = self.option("output")
        encodings = self.option("encoding")
        num_chars = parse_int(self.option("num-chars"), "num-chars")
        in_place = self.option("in-place")

        if in_place and outputs:
            self.line(
                "Incompatible options '-i/--in-place' and '-o/--output'. "
                "Can't edit file in-place and write to an output file."
            )
            return 1

        if len(outputs) == 0:
            outputs = [None for _ in range(len(paths))]

        if not in_place and len(outputs) != len(paths):
            self.line(
                "Number of output files should match the number of input files."
            )
            return 1

        if len(encodings) == 0:
            encodings = [None for _ in range(len(paths))]
        if len(encodings) == 1:
            encodings = [encodings[0] for _ in range(len(paths))]
        elif len(encodings) != len(paths):
            self.line(
                "Number of encodings should be 1 or the same as the "
                "number of input paths."
            )
            return 1

        global_retval = 0
        for path, output, encoding in zip(paths, outputs, encodings):
            retval = self.handle_path(
                path,
                output,
                encoding=encoding,
                verbose=verbose,
                num_chars=num_chars,
            )
            if retval > 0 and global_retval == 0:
                global_retval = retval
            if retval == 1:
                return retval
        return global_retval

    def handle_path(
        self, path, output, encoding=None, num_chars=None, verbose=False
    ):
        encoding = encoding or get_encoding(path)
        dialect = detect_dialect(
            path, num_chars=num_chars, encoding=encoding, verbose=verbose
        )
        if dialect is None:
            self.line("Dialect detection failed.")
            return 1

        if self.option("in-place"):
            return self._in_place(path, dialect, encoding)
        elif output is None:
            return self._to_stdout(path, dialect, encoding)
        return self._to_file(path, output, dialect, encoding)

    def _write_transposed(self, path, stream, dialect, encoding):
        with open(path, "r", newline="", encoding=encoding) as fp:
            read = reader(fp, dialect=dialect)
            rows = list(read)
        rows = list(map(list, zip(*rows)))
        write = writer(stream, dialect="excel")
        for row in rows:
            write.writerow(row)

    def _write_direct(self, path, stream, dialect, encoding):
        with open(path, "r", newline="", encoding=encoding) as fp:
            read = reader(fp, dialect=dialect)
            write = writer(stream, dialect="excel")
            for row in read:
                write.writerow(row)

    def _write_to_stream(self, path, stream, dialect, encoding):
        if self.option("transpose"):
            self._write_transposed(path, stream, dialect, encoding)
        else:
            self._write_direct(path, stream, dialect, encoding)

    def _in_place(self, path, dialect, encoding):
        """In-place mode overwrites the input file, if necessary

        The return value of this method is to be used as the status code of
        the command. A return value of 0 means no edits were made as the file
        was already in the correct format, and a value of 2 means the file was
        modified.

        """
        tmpfd, tmpfname = tempfile.mkstemp(prefix="clevercsv_", suffix=".csv")
        tmpid = os.fdopen(tmpfd, "w", newline="", encoding=encoding)
        self._write_to_stream(path, tmpid, dialect, encoding)
        tmpid.close()

        previous_sha1 = sha1sum(path)
        new_sha1 = sha1sum(tmpfname)
        if previous_sha1 == new_sha1:
            os.unlink(tmpfname)
            return 0

        shutil.move(tmpfname, path)
        return 2

    def _to_stdout(self, path, dialect, encoding):
        stream = io.StringIO(newline="")
        self._write_to_stream(path, stream, dialect, encoding)
        self.overwrite(stream.getvalue())
        stream.close()
        return 0

    def _to_file(self, path, output, dialect, encoding):
        with open(output, "w", newline="", encoding=encoding) as fp:
            self._write_to_stream(path, fp, dialect, encoding)
        return 0
