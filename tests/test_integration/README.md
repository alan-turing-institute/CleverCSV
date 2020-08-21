# Integration Tests

This directory is for the integration tests that evaluate the accuracy of 
dialect detection in CleverCSV. We have a ``data`` folder that contains 
annotated dialects for CSV files scraped from GitHub from repositories with 
the MIT license (allowing their redistribution and use). The 
``test_dialect_detection.py`` script runs CleverCSV on each file for which 
ground truth is available, and writes the file hash to either ``success.log``, 
``failed.log``, or ``error.log``. By keeping these files in Git we can keep 
track of CleverCSVs performance.

Note that runtime should be interpreted very carefully and only when 
experimental conditions are constant, and then generally only as averages.
