#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Detector that models the different dialects as a multi-armed bandit problem and 
uses the UCB algorithm.

**WARNING**: This is currently written as an _inefficient_ proof of concept.

Author: G.J.J. van den Burg
License: See LICENSE file.
Copyright: (c) 2020, The Alan Turing Institute

This file is part of CleverCSV.

"""

import argparse
import clevercsv
import math

from clevercsv.potential_dialects import get_dialects
from clevercsv.detect_pattern import pattern_score
from clevercsv.detect_type import type_score

from utils import get_sample, count_lines


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-f",
        "--full",
        help="Get dialects from full file",
        action="store_true",
        dest="dialects_from_full",
    )
    parser.add_argument(
        "-c",
        "--constant",
        help="Hyperparameter c for the UCB algorithm",
        type=float,
        default=10.0,
    )
    parser.add_argument(
        "-n",
        help="Number of lines to use for detection",
        default=None,
        type=int,
    )
    parser.add_argument(
        "filename", help="File to detect dialect for (.csv or .csv.gz)"
    )
    return parser.parse_args()


def argmax(func, args):
    m, inc = -float("inf"), None
    for a in args:
        if (v := func(a)) > m:
            m, inc = v, a
    return inc


def detector(
    filename, encoding, n_lines=None, dialects_from_full=False, c=10.0,
):
    # Note: n_lines here is the *maximum* number of lines to read. If it is
    # None, in theory the entire file can be read.

    file_lines = count_lines(filename, encoding)
    print(f"File has {file_lines} lines")
    if n_lines is None:
        max_lines = file_lines
    else:
        max_lines = min(n_lines, file_lines)

    lines_start = 100

    if dialects_from_full:
        full_file = get_sample(filename, encoding)
        potential_dialects = get_dialects(
            full_file, test_masked_by_quotes=False
        )
    else:
        sample = get_sample(filename, encoding, n_lines=lines_start)
        potential_dialects = get_dialects(sample, test_masked_by_quotes=False)

    print(f"Identified {len(potential_dialects)} potential dialects.")

    first_sample = get_sample(filename, encoding, n_lines=lines_start)
    sample = first_sample

    scores = {}
    for D in potential_dialects:
        scores[D] = pattern_score(sample, D) * type_score(sample, D)

    means = {D: scores[D] for D in potential_dialects}
    count = {D: 1 for D in potential_dialects}

    D_lines = {D: lines_start for D in potential_dialects}
    for t in range(2, 101):
        estimates = {
            D: means[D] + c * math.sqrt(math.log(t) / count[D])
            for D in potential_dialects
        }
        D_best = argmax(lambda D: estimates[D], estimates.keys())
        D_lines[D_best] += lines_start

        if D_lines[D_best] > max_lines:
            if max_lines == file_lines:
                print("Stopping as end of file is reached")
            else:
                print("Stopping as line limit is reached for incumbent")
            break

        # getting sample can be made more efficient by *adding* to an existing
        # sample
        sample = get_sample(filename, encoding, n_lines=D_lines[D_best])
        # pattern score and type score can be made more efficient as they
        # currently loop over the same data repeatedly
        score = pattern_score(sample, D_best) * type_score(sample, D_best)

        reward = score - scores[D_best]  # reward is increase in score
        scores[D_best] = score

        count[D_best] += 1
        means[D_best] += 1.0 / count[D_best] * (reward - means[D_best])

        print(
            f"Picked: {D_best}.\tMean: {means[D_best]:.8f}.\t"
            f"Estimate: {estimates[D_best]:.8f}\tLines: {D_lines[D_best]}"
        )

        if dialects_from_full:
            continue

        new_dialects = get_dialects(sample, test_masked_by_quotes=False)
        for D in new_dialects:
            if D in potential_dialects:
                continue
            potential_dialects.append(D)
            score = pattern_score(first_sample, D) * type_score(
                first_sample, D
            )
            scores[D] = score
            means[D] = score
            count[D] = 1
            D_lines[D] = lines_start
            print(f"Added dialect {D} (score = {score:.4f})")

    tmp = sorted(((means[D], D) for D in means), reverse=True)
    print("\nTop 10:")
    for i in range(min(len(tmp), 10)):
        D = tmp[i][1]
        print(
            f"\t{D}: Mean = {tmp[i][0]:.4f}. Estimate = {estimates[D]:.4f}."
            f" Lines: {D_lines[D]}"
        )

    return argmax(lambda D: means[D], potential_dialects)


if __name__ == "__main__":
    args = parse_args()
    encoding = clevercsv.utils.get_encoding(args.filename)
    D = detector(
        args.filename,
        encoding,
        n_lines=args.n,
        dialects_from_full=args.dialects_from_full,
        c=args.constant,
    )
    print(D)
