
import os
from setuptools import setup, find_packages
from distutils.extension import Extension

thisdir = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(thisdir, "README.md"), "r") as fid:
    long_description = fid.read()

setup(
    name="ccsv",
    version="0.0.1",
    author="Gertjan van den Burg",
    author_email="gertjanvandenburg@gmail.com",
    description="A clever CSV parser",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/CleverCSV/ccsv",
    packages=find_packages(),
    classifiers=["Programming Language :: Python :: 3"],
    scripts=["bin/clevercsv"],
    ext_modules=[
        Extension(
            "ccsv.cparser",
            sources=["src/cparser.c"],
        ),
        Extension(
            "ccsv.cabstraction",
            sources=["src/abstraction.c"]
            )
    ],
)
