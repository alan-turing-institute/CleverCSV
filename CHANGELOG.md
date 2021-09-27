# Changelog

## Version 0.7.1

* Remove deprecated wrapper functions
* Expand URL regex to support ``localhost:<port>`` urls
* Minor changes to the TypeDetector API
* Add cChardet as optional dependency (fixes 
  [#48](https://github.com/alan-turing-institute/CleverCSV/issues/48))

## Version 0.7.0

* Add a JSON object data type to address a specific failure case 
  ([#37](https://github.com/alan-turing-institute/CleverCSV/issues/37)).
* Add support for timezones for time data type
* Add support for building wheels on non-native architectures 
  ([#39](https://github.com/alan-turing-institute/CleverCSV/issues/39)).
* Add a flag to disable skipping type detection using the command line 
  interface.

## Version 0.6.8

* Add a "bytearray" type to address a specific failure case 
  ([#35](https://github.com/alan-turing-institute/CleverCSV/issues/35)).
* Minor clarifications to licensing.

## Version 0.6.7

* Updates to release process. This version introduces pre-compiled wheels for 
  Python 3.9.

## Version 0.6.6

* Add an `encoding` argument to `write_table` to allow specifying the output 
  encoding. Thanks to @mitchgrogg for reporting [issue 
  #27](https://github.com/alan-turing-institute/CleverCSV/issues/27).

## Version 0.6.5

* Add support for standardizing in-place and standardizing multiple files.
* Add warning on duplicate field names in DictReader
* Add return value to writers to match the standard library.

## Version 0.6.4

* Various speed ups to constructing the list of potential dialects. This 
  removes a costly step of the detection process that will likely add a few 
  more potential dialects, but has the end result of making overall dialect 
  detection faster.

## Version 0.6.3

* Rename wrapper functions to a more coherent naming scheme. Old names will be 
  available until 0.7.0, but now produce a FutureWarning.
* Add ``stream_dicts`` wrapper function.
* Improve handling of file encoding for the ``read_dataframe`` wrapper: 
  detected encoding is now passed on to Pandas.
* Fix handling of optional dependency error for TabView on non-Windows 
  platforms.

## Version 0.6.2

* Update URL regex to avoid catastrophic backtracking and increase 
  performance. See [issue 
  #13](https://github.com/alan-turing-institute/CleverCSV/issues/13) and 
  [issue #15](https://github.com/alan-turing-institute/CleverCSV/issues/15). 
  Thanks to @kaskawu for the fix and @jlumbroso for re-raising the issue.
* Add ``num_chars`` keyword argument to ``read_as_dicts`` and ``csv2df`` 
  wrappers.
* Improve documentation w.r.t. handling large files. Thanks to @jlumbroso for 
  raising this issue.

## Version 0.6.1

* Add an ``explore`` command to the command line application for CleverCSV. 
  This command makes it easy to start exploring a CSV file using the Python 
  interactive shell.

## Version 0.6.0

* Split the package into a "core" and "full" version. This allows users who 
  only need the improved dialect detection functionality to download a version 
  with a smaller footprint. Fixes [issue 
  #10](https://github.com/alan-turing-institute/CleverCSV/issues/10)]. Thanks 
  to @seperman.

## Version 0.5.6

* Fix speed of ``unix_path`` regex used in type detection. ([issue 
  #13](https://github.com/alan-turing-institute/CleverCSV/issues/13)). Thanks 
  to @kaskawu.

## Version 0.5.5

* Add ``stream_csv`` wrapper that returns a generator over rows
* Minor update to the URL type detection
* Documentation updates

## Version 0.5.4

* Fix bugs discovered from fuzz testing ([issue 
  #7](https://github.com/alan-turing-institute/CleverCSV/issues/7))
* Minor changes to readme and code quality

## Version 0.5.3

* Fix using nan as default value when skipping a dialect ([issue 
  #5](https://github.com/alan-turing-institute/CleverCSV/issues/5))

## Version 0.5.2

* Bump version to fix wheel building

## Version 0.5.1

* Bump version to fix wheel building

## Version 0.5.0

* Improve type detection for quoted alphanumeric cells (#4)
* Pass ``strict`` dialect property to parser.

## Version 0.4.7

* Bugfix for ``write_table`` wrapper on Windows.
* Move building Windows platform wheels to Travis.
* Use ``cibuildwheel`` version 1.0.0 for building wheels.

## Version 0.4.6

* Add a wrapper function that writes a table to a CSV file.

## Version 0.4.5

* Update CleverCSV to match updated clikit dependency
* Fix dependency versions for clikit and cleo

## Version 0.4.4

* Update ``standardize`` command to use CRLF line endings on all platforms.
* Add work around for Tabview being unavailable on Windows.
* Remove packaging and dependency management with Poetry.
* Add support for building platform wheels on Travis and AppVeyor.

## Version 0.4.3

* Add optional ``method`` parameter to dialect detector.
* Bugfix for ``clevercsv code`` command when the delimiter is tab.

## Version 0.4.2

* Fix a failing build due to dependency version mismatch

## Version 0.4.1

* Allow underscore in alphanumeric strings
* Update unix path regular expression
* Add more integration tests and log detection method

## Version 0.4.0

* Update URL regular expression and add unit tests
* Add IPv4 type detection
* Add tie-breaker for combined quotechar and escapechar ties

## Version 0.3.7

* Bugfix for console script ``code`` command
* Update readme

## Version 0.3.6

* Cleanly handle failure to detect dialect in console application
* Remove any (partial) support for Python 2

## Version 0.3.5

* Remove Python parser - this speeds up file reading and tie breaking

## Version 0.3.4

* Ensure the C parser is used in the ``reader``.
* Update integration tests to improve error handling
* Readme updates

## Version 0.3.3

* Ensure detected encoding is in the generated Python code for the ``clevercsv 
  code`` command.
* Ensure encoding is detected in ``wrappers.detect_dialect``.
* Bugfix in integration test
* Expand readme

## Version 0.3.2

* Add documentation on [Read the Docs](https://clevercsv.readthedocs.io/)
* Use requirements.txt file for dependencies when packaging

## Version 0.3.1

* Add help description to each CLI command
* Update README
* Add transpose flag for ``standardize`` and ``view`` commands

## Version 0.3.0

* Rewrite console application using Cleo
* Add unit tests for console application
* Add ``detect_dialect`` wrapper function
* Add support for "unix_path" data type in type detection
* Add ``encoding`` and ``num_chars`` options to ``read_csv`` wrapper
* Add ``-p/--pandas`` flag to ``code`` command to generate Pandas output.

## Version 0.2.5

* Rename ``read_as_lol`` to ``read_csv``.

## Version 0.2.4

* Allow setting the number of characters to read
* Simplify printing of skipped potential dialects

## Version 0.2.3

* Add ``read_as_lol`` wrapper function.

## Version 0.2.2

* Add ``code`` command to ``clevercsv`` command line program.

## Version 0.2.1

* Bugfix to update executable to new name

## Version 0.2.0

* Rename package to clevercsv
