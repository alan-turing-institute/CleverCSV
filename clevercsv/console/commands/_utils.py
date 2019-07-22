# -*- coding: utf-8 -*-


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
