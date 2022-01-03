clevercsv-code
==============

SYNOPSIS
--------

clevercsv code **--help**

clevercsv code [**-e** <*encoding>*] [**-i**] [**-n** <*num_char*>] [**-p**] <*path*>

DESCRIPTION
-----------

The code subcommand generates Python code for importing the specified CSV file.
This is especially useful if you don't want to repeatedly detect the dialect of
the same file.

OPTIONS
-------

**-h**, **--help**
    Shows help and exits. Depending on where this option appears it will either
    list the available commands or display help for a specific command.

**-e**, **--encoding** <*encoding*>
    Set the encoding of the CSV file.

**--i**, **--interact**
    Drop into a Python interactive shell.

**-n**, **--num-chars** <*num_chars*>
    Limit the number of characters to read for detection. This will speed up
    detection but may reduce accuracy.

**-p**, **--pandas**
   Write code that imports to a Pandas DataFrame.

EXAMPLES
--------

You can generate the Python code by running::

    $ clevercsv code yourfile.csv

Copy the generated code to a Python script and you're good to go!

SEE ALSO
--------

``clevercsv (1)``, ``clevercsv-detect (1)``, ``clevercsv-explore (1)``,
``clevercsv-standardize (1)``, ``clevercsv-view (1)``
