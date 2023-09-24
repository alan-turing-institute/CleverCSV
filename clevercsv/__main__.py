# -*- coding: utf-8 -*-

"""
Caller for the command line application.

"""

import sys

from ._optional import import_optional_dependency


def main() -> None:
    # Check that necessary dependencies are available
    import_optional_dependency("wilderness")

    # if so, load the actual main function and call it.
    from .console import main as realmain

    sys.exit(realmain())


if __name__ == "__main__":
    main()
