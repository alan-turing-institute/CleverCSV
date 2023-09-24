# -*- coding: utf-8 -*-

"""
Integration tests for dialect detection.

Author: G.J.J. van den Burg

"""

import argparse
import gzip
import json
import multiprocessing
import os
import time
import warnings

from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

import chardet
import termcolor

import clevercsv

from clevercsv.dialect import SimpleDialect

THIS_DIR = os.path.abspath(os.path.dirname(__file__))
SOURCE_DIR = os.path.join(THIS_DIR, "data")
TEST_FILES = os.path.join(SOURCE_DIR, "files")
TEST_DIALECTS = os.path.join(SOURCE_DIR, "dialects")

LOG_SUCCESS = os.path.join(THIS_DIR, "success.log")
LOG_ERROR = os.path.join(THIS_DIR, "error.log")
LOG_FAILED = os.path.join(THIS_DIR, "failed.log")
LOG_METHOD = os.path.join(THIS_DIR, "method.log")
LOG_RUNTIME = os.path.join(THIS_DIR, "runtime.log")

LOG_SUCCESS_PARTIAL = os.path.join(THIS_DIR, "success_partial.log")
LOG_ERROR_PARTIAL = os.path.join(THIS_DIR, "error_partial.log")
LOG_FAILED_PARTIAL = os.path.join(THIS_DIR, "failed_partial.log")
LOG_METHOD_PARTIAL = os.path.join(THIS_DIR, "method_partial.log")
LOG_RUNTIME_PARTIAL = os.path.join(THIS_DIR, "runtime_partial.log")

TIMEOUT = 5 * 60
N_BYTES_PARTIAL = 10000


def log_result(name: str, kind: str, verbose: int, partial: bool) -> None:
    table = {
        "error": (LOG_ERROR, LOG_ERROR_PARTIAL, "yellow"),
        "success": (LOG_SUCCESS, LOG_SUCCESS_PARTIAL, "green"),
        "failure": (LOG_FAILED, LOG_FAILED_PARTIAL, "red"),
    }
    assert kind in table
    outfull, outpartial, color = table[kind]
    fname = outpartial if partial else outfull

    with open(fname, "a") as fp:
        fp.write(name + "\n")
    if verbose:
        termcolor.cprint(name, color=color)


def log_method(name: str, method: str, partial: bool) -> None:
    fname = LOG_METHOD_PARTIAL if partial else LOG_METHOD
    with open(fname, "a") as fp:
        fp.write(f"{name},{method}\n")


def log_runtime(name: str, runtime: float, partial: bool) -> None:
    fname = LOG_RUNTIME_PARTIAL if partial else LOG_RUNTIME
    with open(fname, "a") as fp:
        fp.write(f"{name},{runtime}\n")


def worker(
    args: List[Any], return_dict: Dict[str, Any], **kwargs: Any
) -> None:
    det = clevercsv.Detector()
    filename, encoding, partial = args
    return_dict["error"] = False
    return_dict["dialect"] = None
    return_dict["method"] = None
    return_dict["runtime"] = float("nan")
    with gzip.open(filename, "rt", newline="", encoding=encoding) as fp:
        data = fp.read(N_BYTES_PARTIAL) if partial else fp.read()
        try:
            t = time.time()
            return_dict["dialect"] = det.detect(data, **kwargs)
            return_dict["runtime"] = time.time() - t
            return_dict["method"] = det.method_.value
        except clevercsv.Error:
            return_dict["error"] = True


def run_with_timeout(
    args: Tuple[Any, ...], kwargs: Dict[str, Any], limit: Optional[int]
) -> Tuple[Optional[SimpleDialect], bool, Optional[str], float]:
    manager = multiprocessing.Manager()
    return_dict = manager.dict()
    p = multiprocessing.Process(
        target=worker, args=(args, return_dict), kwargs=kwargs
    )
    p.start()
    p.join(limit)
    if p.is_alive():
        p.terminate()
        return None, True, None, float("nan")
    return (
        return_dict["dialect"],
        return_dict["error"],
        return_dict["method"],
        return_dict["runtime"],
    )


def run_test(
    name: str,
    gz_filename: str,
    annotation: Dict[str, Any],
    verbose: int = 1,
    partial: bool = False,
) -> None:
    if "encoding" in annotation:
        enc = annotation["encoding"]
    else:
        with gzip.open(gz_filename, "rb") as fid:
            enc = chardet.detect(fid.read())["encoding"]

    true_dialect = annotation["dialect"]
    dialect, error, method, runtime = run_with_timeout(
        (gz_filename, enc, partial), {"verbose": verbose > 1}, TIMEOUT
    )
    if error:
        return log_result(name, "error", verbose, partial)

    if dialect is None:
        log_result(name, "failure", verbose, partial)
    elif dialect.delimiter != true_dialect["delimiter"]:
        log_result(name, "failure", verbose, partial)
    elif dialect.quotechar != true_dialect["quotechar"]:
        log_result(name, "failure", verbose, partial)
    elif dialect.escapechar != true_dialect["escapechar"]:
        log_result(name, "failure", verbose, partial)
    else:
        log_result(name, "success", verbose, partial)

    assert method is not None
    log_method(name, method, partial)
    log_runtime(name, runtime, partial)


def load_test_cases() -> List[Tuple[str, str, Dict[str, Any]]]:
    cases = []
    for f in sorted(os.listdir(TEST_FILES)):
        base = f[: -len(".csv.gz")]
        dialect_file = os.path.join(TEST_DIALECTS, base + ".json")
        if not os.path.exists(dialect_file):
            continue
        filename = os.path.join(TEST_FILES, f)
        with open(dialect_file, "r") as fid:
            annotation = json.load(fid)
        if not annotation["filename"] == f[: -len(".gz")]:
            warnings.warn(
                "filename doesn't match! Input file: %s\nDialect file: %s"
                % (filename, dialect_file)
            )
            continue
        if annotation["status"] == "skip":
            continue
        cases.append((base, filename, annotation))
    return cases


def clear_output_files(partial: bool) -> None:
    files = {
        True: [
            LOG_SUCCESS_PARTIAL,
            LOG_FAILED_PARTIAL,
            LOG_ERROR_PARTIAL,
            LOG_METHOD_PARTIAL,
            LOG_RUNTIME_PARTIAL,
        ],
        False: [LOG_SUCCESS, LOG_FAILED, LOG_ERROR, LOG_METHOD, LOG_RUNTIME],
    }
    for filename in files[partial]:
        if os.path.exists(filename):
            os.unlink(filename)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--partial",
        help="Run test with partial file data",
        action="store_true",
    )
    parser.add_argument("-v", "--verbose", help="Be verbose", action="count")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    clear_output_files(args.partial)
    cases = load_test_cases()
    for name, gz_filename, annotation in cases:
        run_test(
            name,
            gz_filename,
            annotation,
            verbose=args.verbose,
            partial=args.partial,
        )


if __name__ == "__main__":
    main()
