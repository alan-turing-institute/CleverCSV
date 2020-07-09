#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

Author: Gertjan van den Burg

"""

import argparse
import json
import matplotlib.pyplot as plt
import os

from collections import defaultdict

from comparison import Record

PLOT_TYPES = ["accuracy", "runtime"]


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("type", help="Plot type to make", choices=PLOT_TYPES)
    parser.add_argument(
        "--result-dir", help="Directory with detection results", required=True
    )
    parser.add_argument(
        "--min-lines",
        help="Minimum number of lines in file",
        default=1000,
        type=int,
    )
    parser.add_argument("-o", "--output", help="File to write figure to")
    parser.add_argument(
        "-d",
        "--delimiter-only",
        help="Only evaluate delimiter detection accuracy",
        action="store_true",
    )
    return parser.parse_args()


def dialect_equal(pred, true):
    if pred is None:
        return False
    return pred == true


def delimiter_equal(pred, true):
    if pred is None:
        return False
    return pred.delimiter == true.delimiter


def compute_accuracy(result_file, checksums, delimiter_only=False):
    correct = 0
    total = 0
    have_checksums = set()
    with open(result_file, "r") as fp:
        for line in fp:
            entry = json.loads(line.strip("\n"))
            record = Record.from_dict(entry)
            if not record.checksum in checksums:
                continue

            if record.status in ["too_small"]:
                continue

            have_checksums.add(record.checksum)

            total += 1
            if record.status in ["failure", "error", "timeout"]:
                continue

            if delimiter_only:
                correct += delimiter_equal(
                    record.pred_dialect, record.true_dialect
                )
            else:
                correct += dialect_equal(
                    record.pred_dialect, record.true_dialect
                )
    if not have_checksums == checksums:
        return None
    return correct / total


def compute_runtime(result_file, checksums):
    runtimes = []
    have_checksums = set()
    with open(result_file, "r") as fp:
        for line in fp:
            entry = json.loads(line.strip("\n"))
            record = Record.from_dict(entry)
            if not record.checksum in checksums:
                continue

            if record.status in ["too_small"]:
                continue

            have_checksums.add(record.checksum)
            runtimes.append(record.runtime)
    if not have_checksums == checksums:
        return None

    return sum(runtimes) / len(runtimes)


def make_plot(
    result_files, checksums, min_lines, plot_type, delimiter_only=False
):
    if not plot_type in PLOT_TYPES:
        raise ValueError(f"Unknown plot type {plot_type}")

    plot_data = defaultdict(lambda: dict(x=[], y=[]))

    for method in result_files:
        for n_lines in result_files[method]:
            if n_lines and n_lines > min_lines:
                continue

            filename = result_files[method][n_lines]
            if plot_type == "accuracy":
                value = compute_accuracy(filename, checksums, delimiter_only)
            else:
                value = compute_runtime(filename, checksums)

            if value is None:
                print(f"Incomplete results for file {filename}")
                continue

            if n_lines is None:
                legend_entry = f"{method} (full)"
                plot_data[legend_entry]["x"] = [1, min_lines]
                plot_data[legend_entry]["y"] = [value, value]
            else:
                legend_entry = f"{method} (partial)"
                plot_data[legend_entry]["x"].append(n_lines)
                plot_data[legend_entry]["y"].append(value)

    fig, ax = plt.subplots(1, 1)
    for key in sorted(plot_data.keys()):
        if "full" in key:
            (line,) = ax.plot(
                plot_data[key]["x"],
                plot_data[key]["y"],
                linestyle="--",
                label=key,
            )
        else:
            obs = {
                x: y for x, y in zip(plot_data[key]["x"], plot_data[key]["y"])
            }
            xs = sorted(obs.keys())
            ys = [obs[x] for x in xs]
            ax.plot(
                xs, ys, "-*", color=line.get_color(), label=key,
            )

    num_files = len(checksums)

    ax.set_xscale("log")
    ax.set_xlabel("Lines used for detection")

    if plot_type == "accuracy":
        pre = f"{'Delimiter' if delimiter_only else 'Detection'} accuracy"
        loc = "best"
        ax.set_ylim(top=1.0)
    else:
        pre = "Average runtime"
        loc = "upper left"

    ax.legend(loc=loc)
    ax.title.set_text(
        f"{pre} for {num_files} files with at least {min_lines} lines"
    )


def load_checksums(files, min_lines):
    checksums = set()
    for result_file in files:
        with open(result_file, "r") as fp:
            for line in fp:
                entry = json.loads(line.strip("\n"))
                record = Record.from_dict(entry)
                if record.line_count < min_lines:
                    continue
                checksums.add(record.checksum)
    return checksums


def main():
    args = parse_args()
    files = os.listdir(args.result_dir)
    paths = [os.path.join(args.result_dir, f) for f in files]

    checksums = load_checksums(paths, args.min_lines)
    print(f"Identified {len(checksums)} files with at least {args.min_lines} lines")

    result_files = {}
    for f in sorted(files):
        if not "_" in f:
            continue
        n_lines = f.split("_")[-1].split(".")[0]
        if n_lines == "full":
            n_lines = None
        else:
            n_lines = int(n_lines)
        method = "_".join(f.split("_")[:-1])
        if not method in result_files:
            result_files[method] = {}
        result_files[method][n_lines] = os.path.join(args.result_dir, f)

    make_plot(
        result_files,
        checksums,
        args.min_lines,
        args.type,
        delimiter_only=args.delimiter_only,
    )
    if args.output is None:
        plt.show()
    else:
        plt.savefig(args.output)


if __name__ == "__main__":
    main()
