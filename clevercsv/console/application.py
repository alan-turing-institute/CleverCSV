# -*- coding: utf-8 -*-

"""
CleverCSV Command line application.

"""

from wilderness import Application

from .. import __version__
from .commands import CodeCommand
from .commands import DetectCommand
from .commands import ExploreCommand
from .commands import StandardizeCommand
from .commands import ViewCommand


class CleverCSVApplication(Application):
    _description = (
        "CleverCSV is a Python library and command line tool for dealing "
        "with messy CSV files. It consists of a number of commands that can "
        "be used to analyze, explore, or standardize a messy CSV file.\n\n"
        "Further help and documentation can be found online at "
        "https://github.com/alan-turing-institute/CleverCSV or "
        "https://clevercsv.readthedocs.io"
    )
    _extra = {
        "Commands": (
            "The following commands are available in CleverCSV:\n\n"
            "clevercsv-code(1)\n"
            "\tGenerate Python code to import a given CSV file\n\n"
            "clevercsv-detect(1)\n"
            "\tDetect the dialect of a CSV file\n\n"
            "clevercsv-explore(1)\n"
            "\tInfer the dialect and open the file in an interactive Python "
            "session\n\n"
            "clevercsv-standardize(1)\n"
            "\tConvert a messy CSV file to one that follows RFC-4180\n\n"
            "clevercsv-view(1)\n"
            "\tDetect the dialect and open the CSV file using TabView"
        ),
        "Authors": (
            "The CleverCSV package was originally written by Gerrit van den "
            "Burg and came out of scientific research on wrangling messy CSV "
            "files by Gerrit van den Burg, Alfredo Nazabal, and Charles "
            "Sutton. This research was conducted at and supported by The "
            "Alan Turing Institute. CleverCSV has since benefitted from a "
            "number of open-source contributors on GitHub."
        ),
        "Reporting Bugs": (
            "If you encounter an issue in CleverCSV, please open an issue "
            "or submit a pull request at "
            "https://github.com/alan-turing-institute/CleverCSV. Please don't "
            "hesitate, you're helping to make this project better for "
            "everyone!"
        ),
        "Notes": (
            "1. CleverCSV GitHub repository\n"
            "   https://github.com/alan-turing-institute/CleverCSV\n\n"
            "2. CleverCSV documentation\n"
            "   https://clevercsv.readthedocs.io\n\n"
            "3. Wrangling Messy CSV Files by Detecting Row and Type Patterns\n"
            "   https://gertjanvandenburg.com/papers/VandenBurg_Nazabal_Sutton_-_Wrangling_Messy_CSV_Files_by_Detecting_Row_and_Type_Patterns_2019.pdf"
        ),
    }

    def __init__(self) -> None:
        super().__init__(
            "clevercsv",
            version=__version__,
            title="CleverCSV command line tool",
            author="G.J.J. van den Burg",
            description=self._description,
            extra_sections=self._extra,
        )

    def register(self) -> None:
        self.add_argument(
            "-V",
            "--version",
            help="Show version and exit",
            action="version",
            version=__version__,
        )
        self.add_argument(
            "-v", "--verbose", help="Enable verbose mode", action="store_true"
        )


def build_application() -> Application:
    app = CleverCSVApplication()
    app.add(DetectCommand())
    app.add(ViewCommand())
    app.add(StandardizeCommand())
    app.add(CodeCommand())
    app.add(ExploreCommand())
    return app
