#
# Makefile for easier installation and cleanup.
#
# Uses self-documenting macros from here:
# http://marmelab.com/blog/2016/02/29/auto-documented-makefile.html

PACKAGE=ccsv
DOC_DIR='./docs/'

.PHONY: help cover

.DEFAULT_GOAL := help

help:
	@grep -E '^[0-9a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) |\
		 awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m\
		 %s\n", $$1, $$2}'

in: inplace
inplace:
	python setup.py build_ext -i

install: ## Install for the current user using the default python command
	python setup.py build_ext --inplace
	python setup.py install --user

install2: ## Install for the current user using the python2 command
	python2 setup.py build_ext --inplace
	python2 setup.py install --user

test: in ## Run nosetests using the default nosetests command
	nosetests --rednose

test2: ## Run nosetests using the nosetests2 command
	python2 setup.py build_ext -i
	nosetests2 -v

cover: test ## Test unit test coverage using default nosetests
	nosetests --with-coverage --cover-package=$(PACKAGE) \
		--cover-erase --cover-inclusive --cover-branches \
		--cover-html --cover-html-dir=cover

clean: ## Clean build dist and egg directories left after install
	rm -rf ./dist ./build ./$(PACKAGE).egg-info
	rm -f MANIFEST

develop: ## Install a development version of the package needed for testing
	python setup.py develop --user

develop2: ## Install a development version of the package needed for testing (python2)
	python2 setup.py develop --user

dist: ## Make Python source distribution
	python setup.py sdist

dist2: ## Make Python 2 source distribution
	python2 setup.py sdist

docs: doc
doc: install ## Build documentation with Sphinx
	$(MAKE) -C $(DOC_DIR) html
