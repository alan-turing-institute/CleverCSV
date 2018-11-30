# SPC-detect
partof: REQ-purpose
###

The ccsv library **shall** provide csv dialect sniffer that uses the data 
consistency measure and normal forms.

- [[SPC-detect-norm]]: detect the dialect using CSV normal forms.
- [[SPC-detect-cons]]: detect the dialect using the data consistency measure


# SPC-detect-cons

The consistency detection method shall use the data consistency measure from 
the paper to detect the dialect.

## [[.pattern]]: Pattern Detection

The ``detect_pattern`` submodule shall contain the pattern score calculation.

## [[.types]]: Type Detection

The ``detect_type`` submodule shall contain the type score calculation.


# SPC-detect-norm

The normal form detection shall use various automated tests to detect the 
dialect.
