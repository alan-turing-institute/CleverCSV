clevercsv-standardize
=====================

SYNOPSIS
--------

clevercsv standardize **--help**

clevercsv standardize [**-e** <*encoding>*] [**-i**] [**-n** <*num_char*>] [**-o** <*output*>] [**-t**] <*path1*> ... [*<pathN*>]

DESCRIPTION
-----------

The standardize subcommand can be used to convert a non-standard CSV file to
the standard RFC-4180 format [1].

When using the **--in-place** option, the return code of CleverCSV can be used
to check whether a file was altered or not. The return code will be 2 when the
file was altered and 0 otherwise.

[1]: https://tools.ietf.org/html/rfc4180

OPTIONS
-------

**-h**, **--help**
    Shows help and exits. Depending on where this option appears it will either
    list the available commands or display help for a specific command.

**-e**, **--encoding** <*encoding*>
      Set the encoding of the CSV file. This will also be used for the output
      file. When multiple input files are provided but only a single encoding
      is given, the encoding will be used for all files. If the encoding is not
      provided it will be detected. (multiple values allowed)

**--i**, **--in-place**
    Standardize and overwrite the input file(s).

**-n**, **--num-chars** <*num_chars*>
    Limit the number of characters to read for detection. This will speed up
    detection but may reduce accuracy.

**-o**, **--output**
    Output file to write to. If omitted, print to stdout. (multiple values
    allowed)

**-t**, **--transpose**
    Transpose the columns of the file before writing.

SEE ALSO
--------

``clevercsv (1)``, ``clevercsv-code (1)``, ``clevercsv-detect (1)``,
``clevercsv-explore (1)``, ``clevercsv-view (1)``
