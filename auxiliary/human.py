#!/usr/bin/env python

"""
This script should be opened within tmux and no other tmux sessions should be 
running.

Author: Gertjan van den Burg

"""

import argparse
import chardet
import codecs
import gzip
import json
import libtmux
import os
import time
import unicodedata


def get_encoding(filename):
    detector = chardet.UniversalDetector()
    final_chunk = False
    blk_size = 65536
    with open(filename, "rb") as fid:
        while (not final_chunk) and (not detector.done):
            chunk = fid.read(blk_size)
            if len(chunk) < blk_size:
                final_chunk = True
            detector.feed(chunk)
    detector.close()
    encoding = detector.result.get("encoding", None)
    return encoding


def load_file(filename, encoding="unknown"):
    if encoding == "unknown":
        encoding = get_encoding(filename)
    with open(filename, "r", newline="", encoding=encoding) as fid:
        try:
            return fid.read()
        except UnicodeDecodeError:
            print(
                "UnicodeDecodeError occurred for file: %s. "
                "This means the encoding was determined incorrectly "
                "or the file is corrupt." % filename
            )
            return None


def is_potential_escapechar(char, encoding):
    as_unicode = codecs.decode(bytes(char, encoding), encoding=encoding)
    ctr = unicodedata.category(as_unicode)
    block = ["!", "?", '"', "'", ".", ",", ";", ":", "%", "*", "&", "#", "/"]
    if ctr == "Po":
        if as_unicode in block:
            return False
        return True
    return False


def get_quotechar_options(data):
    if data is None:
        return set(["q", "a", "b", "t", "n"])
    options = set()
    for x in data:
        if x == '"':
            options.add("q")
        elif x == "'":
            options.add("a")
        elif x == "`":
            options.add("b")
        elif x == "~":
            options.add("t")
    options.add("n")
    return options


def has_initial_space(data, delim):
    if data is None:
        return True
    return "%s " % delim in data


def pairwise(iterable):
    "s - > (s0, s1), (s1, s2), (s2, s3), ..."
    a = iter(iterable)
    b = iter(iterable)
    next(b, None)
    return zip(a, b)


def get_escapechar_options(data, encoding, delim, quotechar):
    if data is None or encoding is None:
        return set(["\\"])
    escapes = set()
    for u, v in pairwise(data):
        if not is_potential_escapechar(u, encoding):
            continue
        if v in [delim, quotechar] and not u in [delim, quotechar]:
            escapes.add(u)
    return escapes


class Asker(object):
    def __init__(self, filename, pane):
        self.filename = filename
        self.opened_vim = False
        self.opened_less = False
        self.pane = pane
        self.note = None
        self.dialect = {
            "delimiter": None,
            "quotechar": None,
            "escapechar": None,
            "skipinitialspace": None,
        }
        self.skip = False
        self.encoding = None
        self.data = None
        self.decompressed_file = None

        if filename.endswith(".gz"):
            self.decompressed_file = os.path.splitext(filename)[0]
            with open(filename, "rb") as fid:
                with open(self.decompressed_file, "wb") as oid:
                    oid.write(gzip.decompress(fid.read()))
            self.filename = self.decompressed_file

    def load_file(self):
        self.encoding = get_encoding(self.filename)
        self.data = load_file(self.filename, encoding=self.encoding)

    def ask_question(self, prompt, key, options=None, highlight_char=None):
        if not self.opened_vim and not self.opened_less:
            self.open_less()
        self.highlight_char(highlight_char)
        prompt = prompt + " " if not prompt.endswith(" ") else prompt
        while True:
            if options is None:
                ans = input(prompt)
            else:
                ans = input("%s[%s] " % (prompt, "/".join(sorted(options))))
            if ans == "quit":
                self.quit()
            elif ans in ["vi", "vim"]:
                self.close()
                self.open_vim()
            elif ans in ["hlt", "hltab"]:
                self.pane.send_keys("/\\t")
            elif ans in ["hls", "hlspace"]:
                self.pane.send_keys("/\\ ")
            elif ans == "skip":
                self.close()
                self.pane.clear()
                self.skip = True
                break
            elif ans == "note":
                self.note = input("Enter note: ").strip()
            elif ans == "none" or ans == "no":
                self.dialect[key] = None
                break
            elif ans == "\\t":
                self.dialect[key] = "\t"
                break
            elif len(ans.strip()) > 1:
                print("Only length 0 or 1 answers are allowed.")
            elif (not options is None) and (not ans.rstrip("\n") in options):
                print("Only these options are allowed: %r" % options)
            else:
                self.dialect[key] = ans.rstrip("\n")
                break

    def process(self):
        print("Annotating file: %s" % self.filename)
        self.ask_question("What is the delimiter?", "delimiter")
        if self.skip:
            return None

        self.load_file()
        if has_initial_space(self.data, self.dialect["delimiter"]):
            hval = "%s " % self.dialect["delimiter"]
            self.ask_question(
                "What is skipinitialspace?",
                "skipinitialspace",
                options=["t", "f"],
                highlight_char=hval,
            )
            if self.skip:
                return None
            self.dialect["skipinitialspace"] = {"t": True, "f": False}[
                self.dialect["skipinitialspace"]
            ]
        else:
            self.dialect["skipinitialspace"] = False

        q_options = get_quotechar_options(self.data)
        if list(q_options) == ["n"]:
            self.dialect["quotechar"] = None
        else:
            q_options.remove("n")
            hval = None
            if "q" in q_options:
                hval = '"'
            elif "a" in q_options:
                hval = "'"
            self.ask_question(
                "What is the quotation mark",
                "quotechar",
                options=q_options,
                highlight_char=hval,
            )
            if not self.dialect["quotechar"] is None:
                self.dialect["quotechar"] = {
                    "Q": '"',
                    "A": "'",
                    "B": "`",
                    "T": "~",
                }[self.dialect["quotechar"].upper()]
        if self.skip:
            return None

        e_options = get_escapechar_options(
            self.data,
            self.encoding,
            self.dialect["delimiter"],
            self.dialect["quotechar"],
        )
        if "n" in e_options:
            raise ValueError("'n' shouldn't be an option in escapechars")
        if len(e_options) == 1 and "\\" in e_options:
            hval = "\\\\"
        else:
            hval = None
        if e_options:
            self.ask_question(
                "What is the escape character?",
                "escapechar",
                options=e_options,
                highlight_char=hval,
            )
        if self.skip:
            return None

        if self.dialect["delimiter"] is None:
            self.dialect["delimiter"] = ""
        if self.dialect["quotechar"] is None:
            self.dialect["quotechar"] = ""
        if self.dialect["escapechar"] is None:
            self.dialect["escapechar"] = ""

        return True

    def highlight_char(self, char=None):
        if char is None:
            return
        self.pane.send_keys("/%s" % char)
        self.pane.send_keys("gg", enter=False, suppress_history=False)
        self.pane.send_keys("n", enter=False, suppress_history=False)

    def open_vim(self):
        self.pane.send_keys("vim %s" % self.filename)
        self.opened_vim = True

    def open_less(self):
        self.pane.send_keys("less -f %s" % self.filename)
        self.opened_less = True

    def close(self):
        if self.opened_less:
            self.close_less()
        elif self.opened_vim:
            self.close_vim()
        self.pane.clear()
        if not self.decompressed_file is None:
            os.unlink(self.decompressed_file)

    def close_vim(self):
        self.pane.send_keys(":q", suppress_history=False)
        time.sleep(0.5)
        self.opened_vim = False

    def close_less(self):
        self.pane.send_keys("q", suppress_history=False)
        time.sleep(0.1)
        self.opened_less = False

    def quit(self):
        self.close()
        self.pane.send_keys("exit")
        print("Thank you.")
        raise SystemExit


def annotate_file(filename, name, tmux_pane):
    print()
    asker = Asker(filename, tmux_pane)
    res = asker.process()
    out = {"filename": name + ".csv", "status": "ok"}
    if not asker.note is None:
        out["note"] = asker.note

    if res is None:
        out["status"] = "skip"
        asker.close()
        return out
    out["dialect"] = asker.dialect
    asker.close()
    return out


def dump_result(output_file, res):
    with open(output_file, "a") as fid:
        json.dump(res, fid, indent=2, sort_keys=True)


def init_tmux():
    tmux_server = libtmux.Server()
    tmux_sess = tmux_server.list_sessions()[-1]
    tmux_win = tmux_sess.attached_window
    less_pane = tmux_win.split_window(attach=False)

    return less_pane


def process(input_dir, output_dir):
    input_files = os.listdir(input_dir)
    input_files.sort()
    input_paths = [os.path.join(input_dir, f) for f in input_files]
    output_files = os.listdir(output_dir)
    output_paths = [os.path.join(output_dir, f) for f in output_files]

    data = []
    for ipath in input_paths:
        base, ext = os.path.splitext(os.path.basename(ipath))
        base_ext = os.path.splitext(base)[1]
        if not (ext == ".csv" or (ext == ".gz" and base_ext == ".csv")):
            print("Warning: non-csv file found in input directory: %s" % ipath)
            continue
        opath = os.path.join(output_dir, base + ".json")
        if opath in output_paths:
            # result file exists
            continue
        name = base if base_ext == "" else os.path.splitext(base)[0]
        data.append((ipath, opath, name))

    if not data:
        return

    less_pane = init_tmux()
    start_time = time.time()

    count = 0
    for ipath, opath, name in data:
        res = annotate_file(ipath, name, less_pane)
        dump_result(opath, res)
        count += 1

        if count % 10 == 0:
            print(
                "\nProgress: %i done out of %i. "
                "This session: %i (%.2f seconds per file)"
                % (
                    count,
                    len(data),
                    count,
                    ((time.time() - start_time) / count),
                )
            )


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_dir", help="Input directory of csv files")
    parser.add_argument("output_dir", help="Output directory of json files")
    return parser.parse_args()


def main():
    args = parse_args()
    process(args.input_dir, args.output_dir)


if __name__ == "__main__":
    main()
