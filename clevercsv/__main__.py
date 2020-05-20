# -*- coding: utf-8 -*-

"""
Caller for the command line application.

"""

import sys

from ._optional import import_optional_dependency


def main():
    # Check that necessary dependencies are available
    import_optional_dependency("cleo")
    import_optional_dependency("clikit")
    import_optional_dependency(
        "tabview", raise_on_missing=not sys.platform == "win32"
    )

    # if so, load the actual main function and call it.
    from .console import main as realmain

    sys.exit(realmain())


if __name__ == "__main__":
    main()
