# CleverCSV Comparison

This directory contains code to compare CleverCSV with common alternatives, 
such as the Python Sniffer and the default method of assuming the comma 
delimiter. It is primarily intended as a toolbox for further development of 
CleverCSV, and is currently focused on improving efficiency on large files 
(see [issue #15](https://github.com/alan-turing-institute/CleverCSV/issues/15)).

The files used for the comparison consists of those used in [the 
paper](https://gertjanvandenburg.com/papers/VandenBurg_Nazabal_Sutton_-_Wrangling_Messy_CSV_Files_by_Detecting_Row_and_Type_Patterns_2019.pdf) 
as test set ([available 
here](https://github.com/alan-turing-institute/CSV_Wrangling/)), as well as 
those collected later and that are used for the [integration 
tests](../tests/test_integration).

In all figures the legend entries ending in ``(full)`` show the results when 
reading the entire file.

## Detection accuracy

These figures show the detection accuracy (delimiter, quote character, and 
escape character) for files with at least *N* lines.

* N = 100

  ![Detection accuracy for files with at least 100 
  lines](./figures/figure_accuracy_100.png)

* N = 1000

  ![Detection accuracy for files with at least 1000 
  lines](./figures/figure_accuracy_1000.png)

* N = 10000

  ![Detection accuracy for files with at least 10000 
  lines](./figures/figure_accuracy_10000.png)

  The dip in accuracy for the Python Sniffer can be explained by the fact that 
  runtime is capped, and timeout is counted as failure.

## Runtime

These figures show the average runtime for dialect detection for each of the 
methods, for files with at least *N* lines. Note that for every method the 
runtime for a single file is capped at two minutes.

* N = 100

  ![Runtime for files with at least 100 
  lines](./figures/figure_runtime_100.png)

* N = 1000

  ![Runtime for files with at least 1000 
  lines](./figures/figure_runtime_1000.png)

* N = 10000

  ![Runtime accuracy for files with at least 10000 
  lines](./figures/figure_runtime_10000.png)

## Delimiter accuracy

These files are similar to the dialect detection accuracy plots above, but 
look only at the delimiter detection accuracy.

* N = 100

  ![Delimiter detection accuracy for files with at least 100 
  lines](./figures/figure_accuracy_delimiter_100.png)

* N = 1000

  ![Delimiter detection accuracy for files with at least 1000 
  lines](./figures/figure_accuracy_delimiter_1000.png)

* N = 10000

  ![Delimiter detection accuracy for files with at least 10000 
  lines](./figures/figure_accuracy_delimiter_10000.png)

