# -*- coding: utf-8 -*-

"""
Caller for the command line application.

"""

import sys


def main():
    from .console import main as realmain

    sys.exit(realmain())


if __name__ == "__main__":
    main()
