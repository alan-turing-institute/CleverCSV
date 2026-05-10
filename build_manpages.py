#!/usr/bin/env python3
from wilderness import build_manpages

from clevercsv.console import build_application

if __name__ == "__main__":
    build_manpages(build_application())
