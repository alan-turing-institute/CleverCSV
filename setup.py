#!/usr/bin/env python
# -*- coding: utf-8 -*-

import io
import os

from setuptools import find_packages, setup
from distutils.extension import Extension

# Package meta-data.
AUTHOR = "Gertjan van den Burg"
DESCRIPTION = "A Python package for handling messy CSV files"
EMAIL = "gertjanvandenburg@gmail.com"
LICENSE = "MIT"
LICENSE_TROVE = "License :: OSI Approved :: MIT License"
NAME = "clevercsv"
REQUIRES_PYTHON = ">=3.6.0"
URL = "https://github.com/alan-turing-institute/CleverCSV"
VERSION = None

# What packages are required for this module to be executed?
REQUIRED = [
    "chardet>=3.0",
    "regex>=2018.11",
]

# When these are changed, update clevercsv/_optional.py accordingly
full_require = [
    "pandas>=0.24.1",
    "tabview>=1.4",
    "cleo>=0.7.6",
    "clikit>=0.4.0",
]

docs_require = ["sphinx", "m2r"]
test_require = full_require + []
dev_require = ["green", "pythonfuzz", "termcolor", "sphinx_rtd_theme"]

# What packages are optional?
EXTRAS = {
    "full": full_require,
    "docs": docs_require,
    "tests": test_require,
    "dev": docs_require + test_require + dev_require,
}

# The rest you shouldn't have to touch too much :)
# ------------------------------------------------
# Except, perhaps the License and Trove Classifiers!
# If you do change the License, remember to change the Trove Classifier for that!

here = os.path.abspath(os.path.dirname(__file__))

# Import the README and use it as the long-description.
# Note: this will only work if 'README.md' is present in your MANIFEST.in file!
try:
    with io.open(os.path.join(here, "README.md"), encoding="utf-8") as f:
        long_description = "\n" + f.read()
except FileNotFoundError:
    long_description = DESCRIPTION

# Load the package's __version__.py module as a dictionary.
about = {}
if not VERSION:
    project_slug = NAME.lower().replace("-", "_").replace(" ", "_")
    with open(os.path.join(here, project_slug, "__version__.py")) as f:
        exec(f.read(), about)
else:
    about["__version__"] = VERSION

# Where the magic happens:
setup(
    name=NAME,
    version=about["__version__"],
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    packages=find_packages(
        exclude=["tests", "*.tests", "*.tests.*", "tests.*"]
    ),
    install_requires=REQUIRED,
    extras_require=EXTRAS,
    include_package_data=True,
    license=LICENSE,
    ext_modules=[
        Extension("clevercsv.cparser", sources=["src/cparser.c"]),
        Extension("clevercsv.cabstraction", sources=["src/abstraction.c"]),
    ],
    entry_points={"console_scripts": ["clevercsv = clevercsv.__main__:main"]},
    classifiers=[
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        LICENSE_TROVE,
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],
)
