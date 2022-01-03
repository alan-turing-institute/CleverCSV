clevercsv-explore
==============

SYNOPSIS
--------

clevercsv explore **--help**

clevercsv explore [**-e** <*encoding>*] [**-n** <*num_char*>] [**-p**] <*path*>

DESCRIPTION
-----------

The explore subcommand allows you to quickly explore a CSV file in an
interactive Python shell. This command detects the dialect of the CSV file and
drops you into a Python interactive shell (REPL), with the CSV file already
loaded.

OPTIONS
-------

**-h**, **--help**
    Shows help and exits. Depending on where this option appears it will either
    list the available commands or display help for a specific command.

**-e**, **--encoding** <*encoding*>
    Set the encoding of the CSV file.

**-n**, **--num-chars** <*num_chars*>
    Limit the number of characters to read for detection. This will speed up
    detection but may reduce accuracy.

**-p**, **--pandas**
   Read code into a Pandas dataframe.

EXAMPLES
--------

To start working with the file loaded as a list of lists, run::

    $ clevercsv explore yourfile.csv

Alternatively, you can read the file as a Pandas dataframe by running::

    $ clevercsv explore -p yourfile.csv

SEE ALSO
--------

``clevercsv (1)``, ``clevercsv-code (1)``, ``clevercsv-detect (1)``,
``clevercsv-standardize (1)``, ``clevercsv-view (1)``
