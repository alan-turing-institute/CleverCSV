<p align="center">
        <img width="60%" src="https://raw.githubusercontent.com/alan-turing-institute/CleverCSV/eea72549195e37bd4347d87fd82bc98be2f1383d/.logo.png">
        <br>
        <a href="https://github.com/alan-turing-institute/CleverCSV/actions">
                <img src="https://github.com/alan-turing-institute/CleverCSV/workflows/build/badge.svg" alt="Github Actions Build Status">
        </a>
        <a href="https://pypi.org/project/clevercsv/">
                <img src="https://badge.fury.io/py/clevercsv.svg" alt="PyPI version">
        </a>
        <a href="https://clevercsv.readthedocs.io/en/latest/?badge=latest">
                <img src="https://readthedocs.org/projects/clevercsv/badge/?version=latest" alt="Documentation Status">
        </a>
        <a href="https://pepy.tech/project/clevercsv">
                <img src="https://pepy.tech/badge/clevercsv" alt="Downloads">
        </a>
        <a href="https://mybinder.org/v2/gh/alan-turing-institute/CleverCSVDemo/master?filepath=CSV_dialect_detection_with_CleverCSV.ipynb">
                <img src="https://mybinder.org/badge_logo.svg" alt="Binder">
        </a>
        <a href="https://rdcu.be/bLVur">
                <img src="https://img.shields.io/badge/DOI-10.1007%2Fs10618--019--00646--y-blue">
        </a>
</p>

*CleverCSV provides a drop-in replacement for the Python* ``csv`` *package 
with improved dialect detection for messy CSV files. It also provides a handy 
command line tool that can standardize a messy file or generate Python code to 
import it.*

**Useful links:**

- [CleverCSV on Github](https://github.com/alan-turing-institute/CleverCSV)
- [CleverCSV on PyPI](https://pypi.org/project/clevercsv/)
- [Demo of CleverCSV on Binder (interactive!)](https://mybinder.org/v2/gh/alan-turing-institute/CleverCSVDemo/master?filepath=CSV_dialect_detection_with_CleverCSV.ipynb)
- [Research Paper on CSV dialect detection 
  (PDF)](https://gertjanvandenburg.com/papers/VandenBurg_Nazabal_Sutton_-_Wrangling_Messy_CSV_Files_by_Detecting_Row_and_Type_Patterns_2019.pdf) 
- [Reproducible Research Repo](https://github.com/alan-turing-institute/CSV_Wrangling/)
- [Blog post on messy CSV files](https://towardsdatascience.com/handling-messy-csv-files-2ef829aa441d)
- [Discussion 
  forum](https://github.com/alan-turing-institute/CleverCSV/discussions): a 
  place to ask questions and share ideas!

---

*Contents:* <a href="#quick-start"><b>Quick Start</b></a> | <a href="#introduction"><b>Introduction</b></a> | <a href="#installation"><b>Installation</b></a> | <a href="#usage"><b>Usage</b></a> | <a href="#python-library">Python Library</a> | <a href="#command-line-tool">Command-Line Tool</a> | <a href="#version-control-integration">Version Control Integration</a> | <a href="#contributing"><b>Contributing</b></a> | <a href="#notes"><b>Notes</b></a>

---

## Quick Start

[Click here](#introduction) to go to the introduction with more details about 
CleverCSV. If you're in a hurry, below is a quick overview of how to get 
started with the CleverCSV Python package and the command line interface. 

For the Python package:

```python
# Import the package
>>> import clevercsv

# Load the file as a list of rows
# This uses the imdb.csv file in the examples directory
>>> rows = clevercsv.read_table('./imdb.csv')

# Load the file as a Pandas Dataframe
# Note that df = pd.read_csv('./imdb.csv') would fail here
>>> df = clevercsv.read_dataframe('./imdb.csv')

# Use CleverCSV as drop-in replacement for the Python CSV module
# This follows the Sniffer example: https://docs.python.org/3/library/csv.html#csv.Sniffer
# Note that csv.Sniffer would fail here
>>> with open('./imdb.csv', newline='') as csvfile:
...     dialect = clevercsv.Sniffer().sniff(csvfile.read())
...     csvfile.seek(0)
...     reader = clevercsv.reader(csvfile, dialect)
...     rows = list(reader)
```

And for the command line interface:

```python
# Install the full version of CleverCSV (this includes the command line interface)
$ pip install clevercsv[full]

# Detect the dialect
$ clevercsv detect ./imdb.csv
Detected: SimpleDialect(',', '', '\\')

# Generate code to import the file
$ clevercsv code ./imdb.csv

import clevercsv

with open("./imdb.csv", "r", newline="", encoding="utf-8") as fp:
    reader = clevercsv.reader(fp, delimiter=",", quotechar="", escapechar="\\")
    rows = list(reader)

# Explore the CSV file as a Pandas dataframe
$ clevercsv explore -p imdb.csv
Dropping you into an interactive shell.
CleverCSV has loaded the data into the variable: df
>>> df
```

## Introduction

- CSV files are awesome! They are lightweight, easy to share, human-readable, 
  version-controllable, and supported by many systems and tools!
- CSV files are terrible! They can have many different formats, multiple 
  tables, headers or no headers, escape characters, and there's no support for 
  recording metadata!

CleverCSV is a Python package that aims to solve some of the pain points of 
CSV files, while maintaining many of the good things. The package 
automatically detects (with high accuracy) the format (*dialect*) of CSV 
files, thus making it easier to simply point to a CSV file and load it, 
without the need for human inspection. In the future, we hope to solve some of 
the other issues of CSV files too.

CleverCSV is [based on 
science](https://gertjanvandenburg.com/papers/VandenBurg_Nazabal_Sutton_-_Wrangling_Messy_CSV_Files_by_Detecting_Row_and_Type_Patterns_2019.pdf). 
We investigated thousands of real-world CSV files to find a robust way to 
automatically detect the dialect of a file. This may seem like an easy 
problem, but to a computer a CSV file is simply a long string, and every 
dialect will give you *some* table. In CleverCSV we use a technique based on 
the patterns of row lengths of the parsed file and the data type of the 
resulting cells. With our method we achieve 97% accuracy for dialect 
detection, with a 21% improvement on non-standard (*messy*) CSV files compared 
to the Python standard library.

We think this kind of work can be very valuable for working data scientists 
and programmers and we hope that you find CleverCSV useful (if there's a 
problem, please open an issue!) Since the academic world counts citations, 
please **cite CleverCSV if you use the package**. Here's a BibTeX entry you 
can use:

```bib
@article{van2019wrangling,
        title = {Wrangling Messy {CSV} Files by Detecting Row and Type Patterns},
        author = {{van den Burg}, G. J. J. and Naz{\'a}bal, A. and Sutton, C.},
        journal = {Data Mining and Knowledge Discovery},
        year = {2019},
        volume = {33},
        number = {6},
        pages = {1799--1820},
        issn = {1573-756X},
        doi = {10.1007/s10618-019-00646-y},
}
```

And of course, if you like the package please *spread the word!* You can do 
this by Tweeting about it 
([#CleverCSV](https://twitter.com/hashtag/clevercsv)) or clicking the ⭐️ [on 
GitHub](https://github.com/alan-turing-institute/CleverCSV)!

## Installation

CleverCSV is available on PyPI. You can install either the full version, which 
includes the command line interface and all optional dependencies, using

```bash
$ pip install clevercsv[full]
```

or you can install a lighter, core version of CleverCSV with

```bash
$ pip install clevercsv
```

## Usage

CleverCSV consists of a Python library and a command line tool called 
``clevercsv``.

### Python Library

We designed CleverCSV to provide a drop-in replacement for the built-in CSV 
module, with some useful functionality added to it. Therefore, if you simply 
want to replace the builtin CSV module with CleverCSV, you can import 
CleverCSV as follows, and use it as you would use the builtin [csv 
module](https://docs.python.org/3/library/csv.html).

```python
import clevercsv
```

CleverCSV provides an improved version of the dialect sniffer in the CSV 
module, but it also adds some useful wrapper functions. These functions 
automatically detect the dialect and aim to make working with CSV files 
easier. We currently have the following helper functions:

* [detect_dialect](https://clevercsv.readthedocs.io/en/latest/source/clevercsv.html#clevercsv.wrappers.detect_dialect): 
  takes a path to a CSV file and returns the detected dialect
* [read_table](https://clevercsv.readthedocs.io/en/latest/source/clevercsv.html#clevercsv.wrappers.read_table): 
  automatically detects the dialect and encoding of the file, and returns the 
  data as a list of rows. A version that returns a generator is also 
  available: 
  [stream_table](https://clevercsv.readthedocs.io/en/latest/source/clevercsv.html#clevercsv.wrappers.stream_table)
* [read_dataframe](https://clevercsv.readthedocs.io/en/latest/source/clevercsv.html#clevercsv.wrappers.read_dataframe): 
  detects the dialect and encoding of the file and then uses 
  [Pandas](https://pandas.pydata.org/) to read the CSV into a DataFrame. Note 
  that this function requires Pandas to be installed.
* [read_dicts](https://clevercsv.readthedocs.io/en/latest/source/clevercsv.html#clevercsv.wrappers.read_dicts): 
  detect the dialect and return the rows of the file as dictionaries, assuming 
  the first row contains the headers. A streaming version called 
  [stream_dicts](https://clevercsv.readthedocs.io/en/latest/source/clevercsv.html#clevercsv.wrappers.stream_dicts) 
  is also available.
* [write_table](https://clevercsv.readthedocs.io/en/latest/source/clevercsv.html#clevercsv.wrappers.write_table): 
  write a table (a list of lists) to a file using the 
  [RFC-4180](https://tools.ietf.org/html/rfc4180) dialect.

Of course, you can also use the traditional way of loading a CSV file, as in 
the Python CSV module:

```python
import clevercsv

with open("data.csv", "r", newline="") as fp:
  # you can use verbose=True to see what CleverCSV does
  dialect = clevercsv.Sniffer().sniff(fp.read(), verbose=False)
  fp.seek(0)
  reader = clevercsv.reader(fp, dialect)
  rows = list(reader)
```

For **large files**, you can speed up detection by supplying a smaller sample 
to the sniffer, for example:
```python
dialect = clevercsv.Sniffer().sniff(fp.read(10000))
```
You can also speed up encoding detection by installing 
[cCharDet](https://github.com/PyYoshi/cChardet), it will automatically be used 
when it is available on the system.

That's the basics! If you want more details, you can look at the code of the 
package, the test suite, or the [API 
documentation](https://clevercsv.readthedocs.io/en/latest/source/modules.html). 
If you run into any issues or have comments or suggestions, please open an 
issue [on GitHub](https://github.com/alan-turing-institute/CleverCSV).

### Command-Line Tool

*To use the command line tool, make sure that you install the full version of 
CleverCSV (see above).*

The ``clevercsv`` command line application has a number of handy features to 
make working with CSV files easier. For instance, it can be used to view a CSV 
file on the command line while automatically detecting the dialect. It can 
also generate Python code for importing data from a file with the correct 
dialect. The full help text is as follows:

```text
USAGE
  clevercsv [-h] [-v] [-V] <command> [<arg1>] ... [<argN>]

ARGUMENTS
  <command>       The command to execute
  <arg>           The arguments of the command

GLOBAL OPTIONS
  -h (--help)     Display this help message.
  -v (--verbose)  Enable verbose mode.
  -V (--version)  Display the application version.

AVAILABLE COMMANDS
  code            Generate Python code for importing the CSV file
  detect          Detect the dialect of a CSV file
  explore         Drop into a Python shell with the CSV file loaded
  help            Display the manual of a command
  standardize     Convert a CSV file to one that conforms to RFC-4180
  view            View the CSV file on the command line using TabView
```

Each of the commands has further options (for instance, the ``code`` and 
``explore`` commands have support for importing the CSV file as a Pandas 
DataFrame). Use ``clevercsv help <command>`` for more information. Below are 
some examples for each command.

Note that each command accepts the ``-n`` or ``--num-chars`` flag to set the 
number of characters used to detect the dialect. This can be especially 
helpful to speed up dialect detection on large files.

#### Code

Code generation is useful when you don't want to detect the dialect of the 
same file over and over again. You simply run the following command and copy 
the generated code to a Python script!

```text
$ clevercsv code imdb.csv

# Code generated with CleverCSV

import clevercsv

with open("imdb.csv", "r", newline="", encoding="utf-8") as fp:
    reader = clevercsv.reader(fp, delimiter=",", quotechar="", escapechar="\\")
    rows = list(reader)
```

We also have a version that reads a Pandas dataframe:

```text
$ clevercsv code --pandas imdb.csv

# Code generated with CleverCSV

import clevercsv

df = clevercsv.read_dataframe("imdb.csv", delimiter=",", quotechar="", escapechar="\\")
```

#### Detect

Detection is useful when you only want to know the dialect.

```text
$ clevercsv detect imdb.csv
Detected: SimpleDialect(',', '', '\\')
```

The ``--plain`` flag gives the components of the dialect on separate lines, 
which makes combining it with ``grep`` easier.

```text
$ clevercsv detect --plain imdb.csv
delimiter = ,
quotechar =
escapechar = \
```

#### Explore

The ``explore`` command is great for a command-line based workflow, or when 
you quickly want to start working with a CSV file in Python. This command 
detects the dialect of a CSV file and starts an interactive Python shell with 
the file already loaded! You can either have the file loaded as a list of 
lists:

```text
$ clevercsv explore milk.csv
Dropping you into an interactive shell.

CleverCSV has loaded the data into the variable: rows
>>>
>>> len(rows)
381
```

or you can load the file as a Pandas dataframe:

```text
$ clevercsv explore -p imdb.csv
Dropping you into an interactive shell.

CleverCSV has loaded the data into the variable: df
>>>
>>> df.head()
                   fn        tid  ... War Western
0  titles01/tt0012349  tt0012349  ...   0       0
1  titles01/tt0015864  tt0015864  ...   0       0
2  titles01/tt0017136  tt0017136  ...   0       0
3  titles01/tt0017925  tt0017925  ...   0       0
4  titles01/tt0021749  tt0021749  ...   0       0

[5 rows x 44 columns]
```

#### Standardize

Use the ``standardize`` command when you want to rewrite a file using the 
[RFC-4180 standard](https://tools.ietf.org/html/rfc4180):

```text
$ clevercsv standardize --output imdb_standard.csv imdb.csv
```

In this particular example the use of the escape character is replaced by 
using quotes.

#### View

This command allows you to view the file in the terminal. The dialect is of 
course detected using CleverCSV! Both this command and the ``standardize`` 
command support the ``--transpose`` flag, if you want to transpose the file 
before viewing or saving:

```text
$ clevercsv view --transpose imdb.csv
```

### Version Control Integration

If you'd like to make sure that you never commit a messy (non-standard) CSV 
file to your repository, you can install a 
[pre-commit](https://pre-commit.com/) hook. First, install pre-commit using 
the [installation instructions](https://pre-commit.com/#install). Next, add 
the following configuration to the ``.pre-commit-config.yaml`` file in your 
repository:

```yaml
repos:
  - repo: https://github.com/alan-turing-institute/CleverCSV-pre-commit
    rev: v0.6.6   # or any later version
    hooks:
      - id: clevercsv-standardize
```

Finally, run ``pre-commit install`` to set up the git hook. Pre-commit will 
now use CleverCSV to standardize your CSV files following 
[RFC-4180](https://tools.ietf.org/html/rfc4180) whenever you commit a CSV file 
to your repository.

## Contributing

If you want to encourage development of CleverCSV, the best thing to do now is 
to *spread the word!*

If you encounter an issue in CleverCSV, please [open an 
issue](https://help.github.com/en/github/managing-your-work-on-github/creating-an-issue) 
or [submit a pull 
request](https://help.github.com/en/github/collaborating-with-issues-and-pull-requests/creating-a-pull-request). 
Don't hesitate, you're helping to make this project better for everyone! If 
GitHub's not your thing but you still want to contact us, you can send an 
email to ``gertjanvandenburg at gmail dot com`` instead. You can also ask 
questions [on Gitter](https://gitter.im/alan-turing-institute/CleverCSV).

Note that all contributions to the project must adhere to the [Code of 
Conduct](https://github.com/alan-turing-institute/CleverCSV/blob/master/CODE_OF_CONDUCT.md).

The CleverCSV package was originally written by [Gertjan van den 
Burg](https://gertjan.dev) and came out of [scientific 
research](https://gertjanvandenburg.com/papers/VandenBurg_Nazabal_Sutton_-_Wrangling_Messy_CSV_Files_by_Detecting_Row_and_Type_Patterns_2019.pdf) 
on wrangling messy CSV files by [Gertjan van den Burg](https://gertjan.dev), 
[Alfredo Nazabal](https://scholar.google.com/citations?user=IanHvT4AAAAJ), and
[Charles Sutton](https://homepages.inf.ed.ac.uk/csutton/).

## Notes

CleverCSV is licensed under the [MIT license](./LICENSE). Please [cite our 
research](https://link.springer.com/article/10.1007/s10618-019-00646-y) if you 
use CleverCSV in your work.

Copyright (c) 2018-2021 [The Alan Turing Institute](https://turing.ac.uk).
