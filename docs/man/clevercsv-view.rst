clevercsv-view
==============

SYNOPSIS
--------

clevercsv view **--help**

clevercsv view [**-e** <*encoding>*][**-n** <*num_char*>] [**-t**] <*path*>

DESCRIPTION
-----------

The view subcommand allows to view a CSV file on the command line, using
TabView.

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

**-t**, **--transpose**
   Transpose the columns of the file before viewing.

SEE ALSO
--------

``clevercsv (1)``, ``clevercsv-code (1)``, ``clevercsv-detect (1)``,
``clevercsv-explore (1)``, ``clevercsv-standardize (1)``
