# -*- coding: utf-8 -*-

"""
Integration tests for dialect detection.

Author: G.J.J. van den Burg

"""

import argparse
import chardet
import clevercsv
import gzip
import json
import multiprocessing
import os
import termcolor
import warnings

THIS_DIR = os.path.abspath(os.path.dirname(__file__))
SOURCE_DIR = os.path.join(THIS_DIR, "data")
TEST_FILES = os.path.join(SOURCE_DIR, "files")
TEST_DIALECTS = os.path.join(SOURCE_DIR, "dialects")

LOG_SUCCESS = os.path.join(THIS_DIR, "success.log")
LOG_ERROR = os.path.join(THIS_DIR, "error.log")
LOG_FAILED = os.path.join(THIS_DIR, "failed.log")

LOG_SUCCESS_PARTIAL = os.path.join(THIS_DIR, "success_partial.log")
LOG_ERROR_PARTIAL = os.path.join(THIS_DIR, "error_partial.log")
LOG_FAILED_PARTIAL = os.path.join(THIS_DIR, "failed_partial.log")


TIMEOUT = 5 * 60
N_BYTES_PARTIAL = 10000


def log_result(name, kind, verbose, partial):
    table = {
        "error": (LOG_ERROR, LOG_ERROR_PARTIAL, "yellow"),
        "success": (LOG_SUCCESS, LOG_SUCCESS_PARTIAL, "green"),
        "failure": (LOG_FAILED, LOG_FAILED_PARTIAL, "red"),
    }
    outfull, outpartial, color = table.get(kind)
    fname = outpartial if partial else outfull

    with open(fname, "a") as fp:
        fp.write(name + "\n")
    if verbose:
        termcolor.cprint(name, color=color)


def worker(args, return_dict, **kwargs):
    det = clevercsv.Detector()
    filename, encoding, partial = args
    with gzip.open(filename, "rt", newline="", encoding=encoding) as fp:
        data = fp.read(N_BYTES_PARTIAL) if partial else fp.read()
        return_dict["dialect"] = det.detect(data, **kwargs)


def run_with_timeout(args, kwargs, limit):
    manager = multiprocessing.Manager()
    return_dict = manager.dict()
    p = multiprocessing.Process(
        target=worker, args=(args, return_dict), kwargs=kwargs
    )
    p.start()
    p.join(limit)
    if p.is_alive():
        p.terminate()
        return None
    return return_dict.get("dialect", None)


def run_test(name, gz_filename, annotation, verbose=True, partial=False):
    if "encoding" in annotation:
        enc = annotation["encoding"]
    else:
        with gzip.open(gz_filename, "rb") as fid:
            enc = chardet.detect(fid.read())["encoding"]

    true_dialect = annotation["dialect"]
    try:
        dialect = run_with_timeout((gz_filename, enc, partial), {}, TIMEOUT)
    except (KeyboardInterrupt, EOFError):
        raise
    except:
        log_result(name, "error", verbose, partial)

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


def load_test_cases():
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


def clear_output_files(partial):
    files = {True: [LOG_SUCCESS_PARTIAL, LOG_FAILED_PARTIAL, 
        LOG_ERROR_PARTIAL],
        False: [LOG_SUCCESS, LOG_FAILED, LOG_ERROR]}
    delete = lambda f : os.unlink(f) if os.path.exists(f) else None
    map(delete, files[partial])

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--partial",
        help="Run test with partial file data",
        action="store_true",
    )
    parser.add_argument(
        "-v", "--verbose", help="Be verbose", action="store_true"
    )
    return parser.parse_args()


def main():
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
