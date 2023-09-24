# -*- coding: utf-8 -*-

import json
import sys
import time

from typing import Any
from typing import Dict

from wilderness import Command

from clevercsv.wrappers import detect_dialect

from ._docs import FLAG_DESCRIPTIONS
from ._utils import parse_int


class DetectCommand(Command):
    _description = "Detect the dialect of a CSV file."

    def __init__(self) -> None:
        super().__init__(
            name="detect",
            title="Detect the dialect of a CSV file",
            description=self._description,
            extra_sections={"CleverCSV": "Part of the CleverCSV suite"},
        )

    def register(self) -> None:
        self.add_argument("path", help="Path to the CSV file")
        self.add_argument(
            "-c",
            "--consistency",
            action="store_true",
            help="Only use the consistency measure for detection.",
            description=(
                "By default, the dialect of CSV files is detected using "
                "atwo-step process. First, a strict set of checks is used to "
                "see if the file adheres to a very basic format (for example, "
                "when all cells in the file are integers). If none of these "
                "checks succeed, the data consistency measure of Van den "
                "Burg, et al. (2019) is used to detect the dialect. With this "
                "option, you can force the detection to always use the data "
                "consistency measure. This can be useful for testing or "
                "research purposes, for instance."
            ),
        )
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
        group = self.add_mutually_exclusive_group()
        group.add_argument(
            "-p",
            "--plain",
            action="store_true",
            help="Print the components of the dialect on separate lines",
        )
        group.add_argument(
            "-j",
            "--json",
            action="store_true",
            help="Print the components of the dialect as a JSON object",
            description=(
                "Print the dialect to standard output in the form of a JSON "
                "object. This object will always have the 'delimiter', "
                "'quotechar', 'escapechar', and 'strict' keys. If "
                "--add-runtime is specified, it will also have a 'runtime' "
                "key."
            ),
        )
        self.add_argument(
            "--no-skip",
            action="store_true",
            help="Don't skip type detection for dialects with a low pattern score",
            description=(
                "The data consistency score used for dialect detection "
                "consists of two components: a pattern score and a type "
                "score. The type score lies between 0 and 1. When computing "
                "the data consistency measures for different dialects, we "
                "skip the computation of the type score if we see that the "
                "pattern score is lower than the best data consistency score "
                "we've seen so far. This option can be used to disable this "
                "behaviour and compute the type score for all dialects. This "
                "is mainly useful for debugging and testing purposes."
            ),
        )
        self.add_argument(
            "--add-runtime",
            action="store_true",
            help="Add the runtime of the detection to the detection output.",
        )

    def handle(self) -> int:
        verbose = self.args.verbose
        num_chars = parse_int(self.args.num_chars, "num-chars")
        method = "consistency" if self.args.consistency else "auto"
        skip = not self.args.no_skip

        t_start = time.time()
        dialect = detect_dialect(
            self.args.path,
            num_chars=num_chars,
            encoding=self.args.encoding,
            verbose=verbose,
            method=method,
            skip=skip,
        )
        runtime = time.time() - t_start

        if dialect is None:
            print("Error: Dialect detection failed.", file=sys.stderr)
            return 1

        if self.args.plain:
            print(f"delimiter = {dialect.delimiter}".strip())
            print(f"quotechar = {dialect.quotechar}".strip())
            print(f"escapechar = {dialect.escapechar}".strip())
            if self.args.add_runtime:
                print(f"runtime = {runtime}")
        elif self.args.json:
            dialect_dict: Dict[str, Any] = dialect.to_dict()
            if self.args.add_runtime:
                dialect_dict["runtime"] = runtime
            print(json.dumps(dialect_dict))
        else:
            print("Detected: " + str(dialect))
            if self.args.add_runtime:
                print(f"Runtime: {runtime:.6f} seconds")
        return 0
