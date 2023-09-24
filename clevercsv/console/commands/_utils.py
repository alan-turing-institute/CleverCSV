# -*- coding: utf-8 -*-

from typing import Any
from typing import List
from typing import Optional

from clevercsv import __version__
from clevercsv.dialect import SimpleDialect


def parse_int(val: Any, name: str) -> Optional[int]:
    """Parse a number to an integer if possible"""
    if val is None:
        return val
    try:
        return int(val)
    except ValueError:
        raise ValueError(
            f"Please provide a number for {name}, instead of {val}"
        )


def generate_code(
    filename: str,
    dialect: SimpleDialect,
    encoding: Optional[str],
    use_pandas: bool = False,
) -> List[str]:
    assert dialect.quotechar is not None
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
        return [
            *base,
            "",
            f'df = clevercsv.read_dataframe("{filename}", delimiter={d}, '
            f"quotechar={q}, escapechar={e})",
            "",
        ]

    enc = "None" if encoding is None else f'"{encoding}"'
    lines = [
        *base,
        "",
        f'with open("{filename}", "r", newline="", encoding={enc}) as fp:',
        "    reader = clevercsv.reader(fp, "
        + f"delimiter={d}, quotechar={q}, escapechar={e})",
        "    rows = list(reader)",
        "",
    ]
    return lines
