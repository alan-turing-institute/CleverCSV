# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# http://www.sphinx-doc.org/en/master/config

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys

sys.path.insert(0, os.path.abspath("."))


# -- Project information -----------------------------------------------------

project = "CleverCSV"
copyright = "2019, The Alan Turing Institute"
author = "G.J.J. van den Burg"


# -- General configuration ---------------------------------------------------

master_doc = 'index'
smartquotes_action = "qe"

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.coverage",
    "sphinx.ext.napoleon",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_rtd_theme"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

# -- Options for manual page output ------------------------------------------

_man_authors = ["Louis-Philippe Véronneau", author]

# Man pages, they are writter to be generated directly by `rst2man` so using
# Sphinx to build them will give weird sections, but if we ever need it it's
# there

# (source start file, name, description, authors, manual section).
man_pages = [
    (
        "man/clevercsv",
        "clevercsv",
        "clevercsv command line interface",
        _man_authors,
        1,
    ),
    (
        "man/clevercsv-code",
        "clevercsv-code",
        "clevercsv code commands",
        _man_authors,
        1,
    ),
    (
        "man/clevercsv-detect",
        "clevercsv-detect",
        "clevercsv detect commands",
        _man_authors,
        1,
    ),
    (
        "man/clevercsv-explore",
        "clevercsv-explore",
        "clevercsv explore commands",
        _man_authors,
        1,
    ),
    (
        "man/clevercsv-standardize",
        "clevercsv-standardize",
        "clevercsv standardize commands",
        _man_authors,
        1,
    ),
    (
        "man/clevercsv-view",
        "clevercsv-view",
        "clevercsv view commands",
        _man_authors,
        1,
    ),
]
