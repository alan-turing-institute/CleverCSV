clevercsv
=========

SYNOPSIS
--------

clevercsv *--help*

clevercsv *--version*

clevercsv [*--verbose*] **command** [*options*]

DESCRIPTION
-----------

Handy command line tool that can standardize messy CSV files or generate Python
code to import them.

SUBCOMMANDS
-----------

clevercsv has five different subcommands:

**code** [*options*]
    Generate Python code for importing the CSV file

**detect** [*options*]
   Detect the dialect of a CSV file

**explore** [*options*]
   Drop into a Python shell with the CSV file loaded

**standardize** [*options*]
   Convert a CSV file to one that conforms to RFC-4180

**view** [*options*]
   View the CSV file on the command line using TabView

For more details on the subcommands, see their respective man pages.

OPTIONS
-------

**-h**, **--help**
    Shows the help and exits. At top level it only lists the subcommands. To
    display the help of a specific subcommand, add the **--help** flag *after*
    said subcommand name.

**-v**, **--verbose**
    Enable verbose mode.

**-V**, **--version**
    Display the version number.

BUGS
----

Bugs can be reported to your distribution's bug tracker or upstream
at https://github.com/alan-turing-institute/CleverCSV/issues

SEE ALSO
--------

``clevercsv-code (1)``, ``clevercsv-detect (1)``, ``clevercsv-explore (1)``,
``clevercsv-standardize (1)``, ``clevercsv-view (1)``
