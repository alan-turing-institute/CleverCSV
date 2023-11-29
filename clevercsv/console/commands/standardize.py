# -*- coding: utf-8 -*-

from __future__ import annotations

import io
import os
import shutil
import sys
import tempfile

from typing import TYPE_CHECKING
from typing import Optional

from wilderness import Command

from clevercsv._types import StrPath
from clevercsv.dialect import SimpleDialect
from clevercsv.encoding import get_encoding
from clevercsv.read import reader
from clevercsv.utils import sha1sum
from clevercsv.wrappers import detect_dialect
from clevercsv.write import writer

if TYPE_CHECKING:
    from clevercsv._types import SupportsWrite

from ._docs import FLAG_DESCRIPTIONS
from ._utils import parse_int


class StandardizeCommand(Command):
    _description = (
        "The standardize command can be used to convert a non-standard "
        "CSVfile to the standard RFC-4180 format [1]. When using the "
        "--in-place option, the return code of CleverCSV can be used to check "
        "whether a file was altered or not. The return code"
        "will be 2 when the file was altered and 0 otherwise.\n\n"
        "[1]: https://tools.ietf.org/html/rfc4180"
    )

    def __init__(self) -> None:
        super().__init__(
            name="standardize",
            title="Convert a CSV file to one that conforms to RFC-4180",
            description=self._description,
            extra_sections={"CleverCSV": "Part of the CleverCSV suite"},
        )

    def register(self) -> None:
        self.add_argument(
            "path", help="Path to one or more CSV file(s)", nargs="+"
        )
        self.add_argument(
            "-e",
            "--encoding",
            action="append",
            help="Set the encoding of the file(s)",
            description=(
                "The file encoding of the given CSV file is automatically "
                "detected using chardet. While chardet is incredibly "
                "accurate, it is not perfect. In the rare cases that it makes "
                "a mistake in detecting the file encoding, you can override "
                "the encoding by providing it through this flag. For this "
                "command, the provided encoding will also be used for the "
                "output file(s). When only one encoding is given, it will be "
                "used for all files given on the command line. When multiple "
                "encodings are given, the number must correspond to the "
                "number of files provided as input."
            ),
            default=[],
        )
        self.add_argument(
            "-E",
            "--target-encoding",
            help="Set the encoding of the output file(s)",
            description=(
                "If ommited, the output file encoding while be the same "
                "as that of the original file."
            ),
            type=str,
        )
        self.add_argument(
            "-i",
            "--in-place",
            help="Standardize and overwrite the input file(s)",
            action="store_true",
        )
        self.add_argument(
            "-n",
            "--num-chars",
            help="Number of characters to use for detection",
            description=FLAG_DESCRIPTIONS["num-chars"],
            type=int,
        )
        self.add_argument(
            "-o",
            "--output",
            action="append",
            help="Output file(s) to write to. If omitted, print to stdout.",
            description=(
                "The output files to write the standardized input files to. "
                "The order of the input files and the order of the output "
                "files should match if this option is used with more than one "
                "input file."
            ),
            default=[],
        )
        self.add_argument(
            "-t",
            "--transpose",
            action="store_true",
            help="Transpose the columns of the input file(s) before writing",
        )

    def handle(self) -> int:
        """Handle the standardize command

        The return value of this method is the exit code of the command, with 0
        meaning success.

        """
        verbose = self.args.verbose
        paths = self.args.path
        outputs = self.args.output
        encodings = self.args.encoding
        num_chars = parse_int(self.args.num_chars, "num-chars")
        in_place = self.args.in_place
        target_encoding = self.args.target_encoding

        if in_place and outputs:
            print(
                "Incompatible options '-i/--in-place' and '-o/--output'. "
                "Can't edit file in-place and write to an output file.",
                file=sys.stderr,
            )
            return 1

        if len(outputs) == 0:
            outputs = [None for _ in range(len(paths))]

        if not in_place and len(outputs) != len(paths):
            print(
                "Number of output files should match the number of input files.",
                file=sys.stderr,
            )
            return 1

        if len(encodings) == 0:
            encodings = [None for _ in range(len(paths))]
        if len(encodings) == 1:
            encodings = [encodings[0] for _ in range(len(paths))]
        elif len(encodings) != len(paths):
            print(
                "Number of encodings should be 1 or the same as the "
                "number of input paths.",
                file=sys.stderr,
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
                target_encoding=target_encoding,
            )
            if retval > 0 and global_retval == 0:
                global_retval = retval
            if retval == 1:
                return retval
        return global_retval

    def handle_path(
        self,
        path: StrPath,
        output: Optional[StrPath],
        encoding: Optional[str] = None,
        num_chars: Optional[int] = None,
        verbose: bool = False,
        target_encoding: Optional[str] = None,
    ) -> int:
        encoding = encoding or get_encoding(path)
        target_encoding = target_encoding or encoding
        dialect = detect_dialect(
            path, num_chars=num_chars, encoding=encoding, verbose=verbose
        )
        if dialect is None:
            print("Error: dialect detection failed.", file=sys.stderr)
            return 1

        if self.args.in_place:
            return self._in_place(path, dialect, encoding, target_encoding)
        elif output is None:
            return self._to_stdout(path, dialect, encoding)
        return self._to_file(path, output, dialect, encoding, target_encoding)

    def _write_transposed(
        self,
        path: StrPath,
        stream: SupportsWrite[str],
        dialect: SimpleDialect,
        encoding: Optional[str],
    ) -> None:
        with open(path, "r", newline="", encoding=encoding) as fp:
            read = reader(fp, dialect=dialect)
            rows = list(read)
        rows = list(map(list, zip(*rows)))
        write = writer(stream, dialect="excel")
        for row in rows:
            write.writerow(row)

    def _write_direct(
        self,
        path: StrPath,
        stream: SupportsWrite[str],
        dialect: SimpleDialect,
        encoding: Optional[str],
    ) -> None:
        with open(path, "r", newline="", encoding=encoding) as fp:
            read = reader(fp, dialect=dialect)
            write = writer(stream, dialect="excel")
            for row in read:
                write.writerow(row)

    def _write_to_stream(
        self,
        path: StrPath,
        stream: SupportsWrite[str],
        dialect: SimpleDialect,
        encoding: Optional[str],
    ) -> None:
        if self.args.transpose:
            self._write_transposed(path, stream, dialect, encoding)
        else:
            self._write_direct(path, stream, dialect, encoding)

    def _in_place(
        self,
        path: StrPath,
        dialect: SimpleDialect,
        encoding: Optional[str],
        target_encoding: Optional[str],
    ) -> int:
        """In-place mode overwrites the input file, if necessary

        The return value of this method is to be used as the status code of
        the command. A return value of 0 means no edits were made as the file
        was already in the correct format, and a value of 2 means the file was
        modified.

        """
        tmpfd, tmpfname = tempfile.mkstemp(prefix="clevercsv_", suffix=".csv")
        tmpid = os.fdopen(tmpfd, "w", newline="", encoding=target_encoding)
        self._write_to_stream(path, tmpid, dialect, encoding)
        tmpid.close()

        previous_sha1 = sha1sum(path)
        new_sha1 = sha1sum(tmpfname)
        if previous_sha1 == new_sha1:
            os.unlink(tmpfname)
            return 0

        shutil.move(tmpfname, path)
        return 2

    def _to_stdout(
        self, path: StrPath, dialect: SimpleDialect, encoding: Optional[str]
    ) -> int:
        stream = io.StringIO(newline="")
        self._write_to_stream(path, stream, dialect, encoding)
        print(stream.getvalue(), end="")
        stream.close()
        return 0

    def _to_file(
        self,
        path: StrPath,
        output: StrPath,
        dialect: SimpleDialect,
        encoding: Optional[str],
        target_encoding: Optional[str],
    ) -> int:
        with open(output, "w", newline="", encoding=target_encoding) as fp:
            self._write_to_stream(path, fp, dialect, encoding)
        return 0
