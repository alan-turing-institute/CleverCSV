#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Determine file encodings

Author: Gertjan van den Burg

"""

import argparse
import chardet
import gzip
import json
import os
import tqdm


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dialect-dir", help="Directory with dialect files", required=True,
    )
    parser.add_argument(
        "--file-dir", help="Directory with CSV files", required=True
    )
    parser.add_argument(
        "--output-file", help="Output file to store results", required=True
    )
    return parser.parse_args()


def load_cache(cache_file):
    cache = {}
    if not os.path.exists(cache_file):
        return cache
    with open(cache_file, "r") as fp:
        for line in fp:
            entry = json.loads(line.strip())
            checksum = entry["checksum"]
            cache[checksum] = entry
    return cache


def load_json(filename):
    with open(filename, "r") as fp:
        return json.load(fp)


def checksum_from_file(filename):
    base = os.path.basename(filename)
    if base.endswith(".csv.gz"):
        return base[: -len(".csv.gz")]
    return base[: -len(".csv")]


def get_encoding(filename, dialect_dir):
    checksum = checksum_from_file(filename)

    dialect_file = os.path.join(dialect_dir, checksum + ".json")
    if os.path.exists(dialect_file):
        annotation = load_json(dialect_file)
        if "encoding" in annotation:
            return annotation["encoding"]

    opener = gzip.open if filename.endswith(".gz") else open
    detector = chardet.UniversalDetector()
    blk_size = 65536
    final_chunk = False
    with opener(filename, "rb") as fp:
        while (not final_chunk) and (not detector.done):
            chunk = fp.read(blk_size)
            if len(chunk) < blk_size:
                final_chunk = True
            detector.feed(chunk)
    detector.close()
    enc = detector.result["encoding"]
    return enc


def main():
    args = parse_args()
    cache = load_cache(args.output_file)
    for f in tqdm.tqdm(sorted(os.listdir(args.file_dir))):
        filename = os.path.join(args.file_dir, f)
        checksum = checksum_from_file(filename)
        if checksum in cache:
            continue

        encoding = get_encoding(filename, args.dialect_dir)
        with open(args.output_file, "a") as fp:
            entry = dict(checksum=checksum, encoding=encoding)
            fp.write(json.dumps(entry))
            fp.write("\n")


if __name__ == "__main__":
    main()
