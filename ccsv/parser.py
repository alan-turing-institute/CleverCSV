# -*- coding: utf-8 -*-

"""
Our CSV parser.

Author: Gertjan van den Burg

"""


def parse_data(
    data, dialect=None, delimiter=None, quotechar=None, escapechar=None
):
    """
    Parse a CSV file given as a string by ``data`` into a list of lists.

    This function automatically takes double quotes into account, uses 
    universal newlines, and can deal with quotes that start *inside* a cell.  
    Quotes are only stripped from cells if they occur at the start and the end 
    of the cell.

    Notes
    -----

    (1) We only interpret the escape character if it precedes the provided 
    delimiter, quotechar, or itself. Otherwise, the escape character does not 
    serve any purpose, and should not be dropped automatically.

    (2) For some reason the Python test suite places this escape character 
    *inside* the preceding quoted block. This seems counterintuitive and 
    incorrect and thus this behavior has not been duplicated.

    """
    if not dialect is None:
        delimiter = dialect.delimiter if delimiter is None else delimiter
        quotechar = dialect.quotechar if quotechar is None else quotechar
        escapechar = dialect.escapechar if escapechar is None else escapechar

    quote_cond = lambda c, q: q and c.startswith(q) and c.endswith(q)

    in_quotes = False
    in_escape = False
    i = 0
    row = []
    field = ""
    end_row = False
    end_field = False
    s = None
    while i < len(data):
        s = data[i]
        if s == quotechar:
            if in_escape:
                in_escape = False
            elif not in_quotes:
                in_quotes = True
            else:
                if i + 1 < len(data) and data[i + 1] == quotechar:
                    i += 1
                else:
                    in_quotes = False
            field += s
        elif s in ["\r", "\n"]:
            if in_quotes:
                field += s
            elif field == "" and row == []:
                pass
            else:
                end_row = True
                end_field = True
        elif s == delimiter:
            if in_escape:
                in_escape = False
                field += s
            elif in_quotes:
                field += s
            else:
                end_field = True
        elif s == escapechar:
            if in_escape:
                field += s
                in_escape = False
            else:
                in_escape = True
        else:
            if in_escape:
                field += escapechar
                in_escape = False
            field += s

        if end_field:
            if quote_cond(field, quotechar):
                field = field[1:-1]
            row.append(field)
            field = ""
            end_field = False

        if end_row:
            yield row
            row = []
            end_row = False

        i += 1

    if quote_cond(field, quotechar):
        field = field[1:-1]
    elif in_quotes:
        if field.startswith(quotechar):
            field = field[1:]
        s = ""
    if not s in ["\r", "\n", None]:
        row.append(field)
        yield row

