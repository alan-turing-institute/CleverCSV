# -*- coding: utf-8 -*-

FLAG_DESCRIPTIONS = {
    "encoding": (
        "The file encoding of the given CSV file is automatically "
        "detected using chardet. While chardet is incredibly "
        "accurate, it is not perfect. In the rare cases that it makes "
        "a mistake in detecting the file encoding, you can override "
        "the encoding by providing it through this flag. Moreover, "
        "when you have a number of CSV files with a known file "
        "encoding, you can use this option to speed up the code "
        "generation process."
    ),
    "num-chars": (
        "On large CSV files, dialect detection can sometimes be a bit "
        "slow due to the large number of possible dialects to "
        "consider. To alleviate this, you can limit the number of "
        "characters to use for detection.\n\n"
        "One aspect to keep in mind is that CleverCSV may need to "
        "read a specific number of characters to be able to correctly "
        "infer the dialect. For example, in the ``imdb.csv`` file "
        "in the GitHub repository, the correct dialect can only "
        "be found after at least 66 lines of the file are read. "
        "Therefore, if there is availability to run CleverCSV on "
        "the entire file, that is generally recommended."
    ),
}
