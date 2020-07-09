# -*- coding: utf-8 -*-

"""Comparison code for partial file reads

This is the main script to run dialect detection comparison between different 
methods. In particular, this script evaluates how well each method can detect 
the dialect using a limited number of lines. This can hopefully lead to more 
efficient implementations of CleverCSV's core algorithm for large files.

Author: G.J.J. van den Burg
License: See LICENSE file
Copyright: 2020, The Alan Turing Institute

"""

import argparse
import dataclasses
import enum
import json
import multiprocessing
import os
import time
import sys

from detector_clevercsv_grow import detector as grow_detector
from detector_clevercsv import detector as ccsv_detector
from detector_simple import detector as simple_detector
from detector_sniffer import detector as sniff_detector
from utils import DetectionError, count_lines

TIMEOUT = 120
METHODS = {
    "clevercsv": ccsv_detector,
    "clevercsv_grow": grow_detector,
    "simple": simple_detector,
    "sniffer": sniff_detector,
}


DetectionStatus = enum.Enum(
    "DetectionStatus", "success failure error timeout too_small"
)


@dataclasses.dataclass
class Dialect:
    delimiter: str
    quotechar: str
    escapechar: str

    @classmethod
    def from_dict(self, d):
        return Dialect(**d)

    def to_dict(self):
        keys = ["delimiter", "quotechar", "escapechar"]
        return {k: getattr(self, k) for k in keys}


@dataclasses.dataclass
class Record:
    checksum: str
    status: DetectionStatus
    line_count: int
    runtime: float
    true_dialect: Dialect
    pred_dialect: Dialect

    @classmethod
    def from_dict(self, d):
        true_dialect = Dialect.from_dict(d["true_dialect"])
        pred_dialect = d.get("pred_dialect", None)
        if pred_dialect:
            pred_dialect = Dialect.from_dict(d["pred_dialect"])
        dd = {k: v for k, v in d.items()}
        dd["true_dialect"] = true_dialect
        dd["pred_dialect"] = pred_dialect
        return Record(**dd)

    def to_dict(self):
        keys = ["checksum", "status", "line_count", "runtime"]
        d = {k: getattr(self, k) for k in keys}
        d["true_dialect"] = self.true_dialect.to_dict()
        if self.pred_dialect is None:
            d["pred_dialect"] = None
        else:
            d["pred_dialect"] = self.pred_dialect.to_dict()
        d["status"] = d["status"].name
        return d


def wrap_detector(func, args, return_dict, **kwargs):
    """Wrap the detection function to handle detection errors"""

    status = DetectionStatus.success
    t_start = time.time()
    try:
        dialect = func(*args, **kwargs)
    except DetectionError:
        dialect = None
        status = DetectionStatus.failure
    finally:
        t_stop = time.time()
    runtime = t_stop - t_start
    return_dict["dialect"] = dialect
    return_dict["status"] = status
    return_dict["runtime"] = runtime


class DetectorRunner:
    def __init__(
        self,
        detector_name,
        detector_func,
        output_file,
        n_lines=None,
        verbose=0,
    ):
        self.name = detector_name
        self.detector_func = detector_func
        self.n_lines = n_lines

        self.cache_file = output_file
        self.cache = self.load_cache(self.cache_file)

        self.verbosity = verbose

    def load_cache(self, filename):
        cache = {}
        if not os.path.exists(filename):
            return cache
        with open(filename, "r") as fp:
            for line in fp:
                entry = json.loads(line.strip())
                cache[entry["checksum"]] = Record.from_dict(entry)
        return cache

    def extract_checksum(self, filename):
        base = os.path.basename(filename)
        if base.endswith(".csv.gz"):
            return base[: -len(".csv.gz")]
        return base[: -len(".csv")]

    def run_with_timeout(self, filename, encoding):
        manager = multiprocessing.Manager()
        return_dict = manager.dict()
        p = multiprocessing.Process(
            target=wrap_detector,
            args=(self.detector_func, (filename, encoding), return_dict),
            kwargs={"n_lines": self.n_lines},
        )
        p.start()
        p.join(TIMEOUT)
        if p.is_alive():
            p.terminate()
            return None, DetectionStatus.timeout, TIMEOUT
        pred_dialect = return_dict["dialect"]
        status = return_dict["status"]
        runtime = return_dict["runtime"]
        return pred_dialect, status, runtime

    def detector_wrapper(self, filename, encoding):
        checksum = self.extract_checksum(filename)
        line_count = count_lines(filename, encoding)
        if self.n_lines and line_count < self.n_lines:
            return Record(
                checksum=checksum,
                status=DetectionStatus.too_small,
                line_count=line_count,
                runtime=None,
                true_dialect=None,
                pred_dialect=None,
            )
        pred_dialect, status, runtime = self.run_with_timeout(
            filename, encoding
        )
        if pred_dialect:
            pred_dialect = Dialect.from_dict(pred_dialect)
        return Record(
            checksum=checksum,
            status=status,
            line_count=line_count,
            runtime=runtime,
            true_dialect=None,
            pred_dialect=pred_dialect,
        )

    def cached_detection(self, filename, encoding, true_dialect):
        checksum = self.extract_checksum(filename)
        if checksum in self.cache:
            return self.cache[checksum]

        record = self.detector_wrapper(filename, encoding)
        record.true_dialect = true_dialect

        with open(self.cache_file, "a") as fp:
            fp.write(json.dumps(record.to_dict()))
            fp.write("\n")

        return record

    def run(self, targets):
        for filename, true_dialect, encoding in targets:
            if self.verbosity > 0:
                print(
                    f"[{self.name}-{self.n_lines}]: {self.extract_checksum(filename)}",
                    flush=True,
                )
            self.cached_detection(filename, encoding, true_dialect)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dialect-dir", help="Directory with dialect files", required=True,
    )
    parser.add_argument(
        "--file-dir", help="Directory with CSV files", required=True
    )
    parser.add_argument(
        "--n-lines",
        help="Number of lines to read (smaller files are skipped, omitted means all lines)",
        type=int,
        default=None,
    )
    parser.add_argument(
        "--output-file", help="File to store detection results", required=True,
    )
    parser.add_argument(
        "--method",
        help="Detection method to run",
        choices=list(METHODS.keys()),
        required=True,
    )
    parser.add_argument(
        "--encoding-cache",
        help="Cache file with file encodings",
        required=True,
    )
    parser.add_argument("-v", "--verbose", action="count", default=0)
    return parser.parse_args()


def load_targets(files_dir, dialects_dir, encodings_file, verbose=0):
    """Load test cases from directory

    This function loads the test cases based on the available files and ground 
    truth dialects. It also determines and caches the encoding of the file, so 
    that we don't have to do that repeatedly.

    """
    log = lambda *a, **kw: print(*a, **kw) if verbose > 0 else None

    encodings_cache = {}
    if os.path.exists(encodings_file):
        with open(encodings_file, "r") as fp:
            for line in fp:
                entry = json.loads(line.strip())
                encodings_cache[entry["checksum"]] = entry["encoding"]

    targets = []
    log("Loading test cases ...")
    for f in sorted(os.listdir(files_dir)):
        base = os.path.basename(f)
        if base.endswith(".csv.gz"):
            checksum = base[: -len(".csv.gz")]
        else:
            checksum = base[: -len(".csv")]

        # Skip files for which we don't have a dialect file
        dialect_file = os.path.join(dialects_dir, checksum + ".json")
        if not os.path.exists(dialect_file):
            continue

        # Load the ground truth annotation
        filename = os.path.join(files_dir, f)
        with open(dialect_file, "r") as fid:
            annotation = json.load(fid)

        # Check that the filename in the annotation matches
        csvfile = f[: -len(".gz")] if f.endswith(".gz") else f
        if not annotation["filename"] == csvfile:
            print(
                "filename doesn't match! Input file: %s\nDialect file: %s"
                % (filename, dialect_file),
                file=sys.stderr,
            )
            continue

        if annotation["status"] == "skip":
            continue

        # Load the dialect
        dialect = annotation["dialect"]
        dialect = {
            k: dialect[k] for k in ["delimiter", "quotechar", "escapechar"]
        }
        dialect = Dialect.from_dict(dialect)

        # Retrieve the encoding
        encoding = encodings_cache[checksum]

        targets.append((filename, dialect, encoding))
    return targets


def main():
    args = parse_args()

    targets = load_targets(
        args.file_dir,
        args.dialect_dir,
        args.encoding_cache,
        verbose=args.verbose,
    )

    method_name = args.method
    method_func = METHODS[method_name]

    runner = DetectorRunner(
        method_name,
        method_func,
        args.output_file,
        n_lines=args.n_lines,
        verbose=args.verbose,
    )
    runner.run(targets)


if __name__ == "__main__":
    main()
