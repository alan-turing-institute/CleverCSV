# Makefile for comparison
#
# Author: G.J.J. van den Burg
# Copyright (c) The Alan Turing Institute
# License: MIT
# Date: 2019-07-19
#

FILE_DIR=./files
DIALECT_DIR=./dialects
RESULT_DIR=./results
FIGURE_DIR=./figures

NUM_LINES = 1 2 3 4 5 6 7 8 9 \
	    10 20 30 40 50 60 70 80 90 \
	    100 200 300 400 500 600 700 800 900 \
	    1000 2000 3000 4000 5000 6000 7000 8000 9000 \
	    10000
METHODS = simple sniffer clevercsv clevercsv_grow
FIGURES = $(FIGURE_DIR)/figure_accuracy_100.png \
	  $(FIGURE_DIR)/figure_runtime_100.png \
	  $(FIGURE_DIR)/figure_accuracy_1000.png \
	  $(FIGURE_DIR)/figure_runtime_1000.png \
	  $(FIGURE_DIR)/figure_accuracy_10000.png \
	  $(FIGURE_DIR)/figure_runtime_10000.png \
	  $(FIGURE_DIR)/figure_accuracy_delimiter_100.png \
	  $(FIGURE_DIR)/figure_accuracy_delimiter_1000.png \
	  $(FIGURE_DIR)/figure_accuracy_delimiter_10000.png

TARGETS =

.PHONY: all comparison result-dir 

all: comparison

result-dir:
	mkdir -p $(RESULT_DIR)

############
# Encoding #
############

.PRECIOUS: $(RESULT_DIR)/encodings.json

.PHONY: encodings

encodings: encodings.json

encodings.json: ./determine_encodings.py | result-dir
	python $< --output-file $@ --dialect-dir $(DIALECT_DIR) \
		--file-dir $(FILE_DIR)

#####################
# Dialect Detection #
#####################

define run-detector-lines
$(RESULT_DIR)/$(1)_$(2).json: ./comparison.py encodings.json |\
	result-dir
	python $$< \
		--dialect-dir $(DIALECT_DIR) \
		--file-dir $(FILE_DIR) \
		--encoding-cache encodings.json \
		--output-file $$@ \
		--n-lines $(2) \
		--method $(1) \
		--verbose
	TARGETS += $(RESULT_DIR)/$(1)_$(2).json
endef

define run-detector-full
$(RESULT_DIR)/$(1)_full.json: ./comparison.py encodings.json |\
	result-dir
	python $$< \
		--dialect-dir $(DIALECT_DIR) \
		--file-dir $(FILE_DIR) \
		--encoding-cache encodings.json \
		--output-file $$@ \
		--method $(1) \
		--verbose
	TARGETS += $(RESULT_DIR)/$(1)_full.json
endef

$(foreach method,$(METHODS),$(eval $(call run-detector-full,$(method))))

$(foreach method,$(METHODS),$(foreach num_lines,$(NUM_LINES),\
       	$(eval $(call run-detector-lines,$(method),$(num_lines)))))

comparison: $(TARGETS)

.PRECIOUS: $(TARGETS)

.PHONY: $(TARGETS)

###########
# Figures #
###########

.PHONY: figures

figures: $(FIGURES)

figure_accuracy_100.png: ./make_plot.py $(TARGETS)
	python $< --result-dir $(RESULT_DIR) --min-lines 100 -o $@ accuracy

figure_runtime_100.png: ./make_plot.py $(TARGETS)
	python $< --result-dir $(RESULT_DIR) --min-lines 100 -o $@ runtime

figure_accuracy_1000.png: ./make_plot.py $(TARGETS)
	python $< --result-dir $(RESULT_DIR) --min-lines 1000 -o $@ accuracy

figure_runtime_1000.png: ./make_plot.py $(TARGETS)
	python $< --result-dir $(RESULT_DIR) --min-lines 1000 -o $@ runtime

figure_accuracy_10000.png: ./make_plot.py $(TARGETS)
	python $< --result-dir $(RESULT_DIR) --min-lines 10000 -o $@ accuracy

figure_runtime_10000.png: ./make_plot.py $(TARGETS)
	python $< --result-dir $(RESULT_DIR) --min-lines 10000 -o $@ runtime

figure_accuracy_delimiter_100.png: ./make_plot.py $(TARGETS)
	python $< --result-dir $(RESULT_DIR) --min-lines 100 -o $@ -d accuracy

figure_accuracy_delimiter_1000.png: ./make_plot.py $(TARGETS)
	python $< --result-dir $(RESULT_DIR) --min-lines 1000 -o $@ -d accuracy

figure_accuracy_delimiter_10000.png: ./make_plot.py $(TARGETS)
	python $< --result-dir $(RESULT_DIR) --min-lines 10000 -o $@ -d accuracy


############
# Clean up #
############

check_clean:
	@echo -n "Are you sure? [y/N]" && read ans && [ $$ans == y ]

clean: check_clean
	rm -f $(TARGETS)
	rm -f $(FIGURES)
	rm -f encodings.json
