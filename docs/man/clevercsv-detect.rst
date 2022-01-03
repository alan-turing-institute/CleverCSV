clevercsv-detect
==============

SYNOPSIS
--------

clevercsv detect **--help**

clevercsv detect [**-c**] [**-e** <*encoding>*] [**-n** <*num_char*>] [**-p**] [**-j**] [**--no-skip**] <*path*>

DESCRIPTION
-----------

The detect subcommand detects the dialect of a given CSV file.

OPTIONS
-------

**-h**, **--help**
    Shows help and exits. Depending on where this option appears it will either
    list the available commands or display help for a specific command.

**-c**, **--consitency**
    Use only the consistency measure for detection.

**-e**, **--encoding** <*encoding*>
    Set the encoding of the CSV file.

**-n**, **--num-chars** <*num_chars*>
    Limit the number of characters to read for detection. This will speed up
    detection but may reduce accuracy.

**-p**, **--plain**
    Print the components of the dialect on separate lines.

**-j**, **--json**
    Print the components of the dialect as a JSON object.

**--no-skip**
    Don't skip type detection for dialects with low pattern score.

SEE ALSO
--------

``clevercsv (1)``, ``clevercsv-code (1)``, ``clevercsv-explore (1)``,
``clevercsv-standardize (1)``, ``clevercsv-view (1)``
