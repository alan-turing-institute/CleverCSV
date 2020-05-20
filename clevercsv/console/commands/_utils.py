# -*- coding: utf-8 -*-

from clevercsv import __version__


def parse_int(val, name):
    """Parse a number to an integer if possible"""
    if val is None:
        return val
    try:
        return int(val)
    except ValueError:
        raise ValueError(
            f"Please provide a number for {name}, instead of {val}"
        )


def generate_code(filename, dialect, encoding, use_pandas=False):
    d = '"\\t"' if dialect.delimiter == "\t" else f'"{dialect.delimiter}"'
    q = '"%s"' % (dialect.quotechar.replace('"', '\\"'))
    e = repr(f"{dialect.escapechar}").replace("'", '"')
    base = [
        "",
        f"# Code generated with CleverCSV version {__version__}",
        "",
        "import clevercsv",
    ]
    if use_pandas:
        return base + [
            "",
            f'df = clevercsv.read_dataframe("{filename}", delimiter={d}, quotechar={q}, escapechar={e})',
            "",
        ]

    enc = "None" if encoding is None else f'"{encoding}"'
    lines = base + [
            "",
            f'with open("{filename}", "r", newline="", encoding={enc}) as fp:',
            "    reader = clevercsv.reader(fp, "
            + f"delimiter={d}, quotechar={q}, escapechar={e})",
            "    rows = list(reader)",
            "",
    ]
    return lines
