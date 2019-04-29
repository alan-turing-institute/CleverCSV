import os
from setuptools import setup, find_packages
from distutils.extension import Extension

thisdir = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(thisdir, "README.md"), "r") as fid:
    long_description = fid.read()

setup(
    name="clevercsv",
    version="0.1.1",
    author="Gertjan van den Burg",
    author_email="gertjanvandenburg@gmail.com",
    description="A clever CSV parser",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/alan-turing-institute/CleverCSV",
    packages=find_packages(),
    classifiers=["Programming Language :: Python :: 3"],
    scripts=["bin/clevercsv"],
    install_requires=["regex"],
    ext_modules=[
        Extension("ccsv.cparser", sources=["src/cparser.c"]),
        Extension("ccsv.cabstraction", sources=["src/abstraction.c"]),
    ],
)
