# -*- coding: utf-8 -*-

"""
CleverCSV Command line application.

"""

from cleo import Application

from .. import __version__
from .config import Config
from .commands import (
    CodeCommand,
    DetectCommand,
    StandardizeCommand,
    ViewCommand,
)


def build_application():
    config = Config("clevercsv", __version__)
    app = Application(config=config, complete=False)
    app.add(ViewCommand())
    app.add(DetectCommand())
    app.add(StandardizeCommand())
    app.add(CodeCommand())
    return app
