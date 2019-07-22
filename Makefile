# Makefile for easier installation and cleanup.
#
# Uses self-documenting macros from here:
# http://marmelab.com/blog/2016/02/29/auto-documented-makefile.html

PACKAGE=clevercsv
DOC_DIR='./docs/'

.PHONY: help cover dist

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

test: in ## Run nosetests using the default nosetests command
	poetry run green -v ./tests/test_unit

integration: install ## Run integration tests with nose
	python ./tests/test_integration/test_dialect_detection.py -v

integration_partial: install ## Run partial integration test with nose
	python ./tests/test_integration/test_dialect_detection.py -v --partial

cover: test ## Test unit test coverage using default nosetests
	nosetests --with-coverage --cover-package=$(PACKAGE) \
		--cover-erase --cover-inclusive --cover-branches \
		--cover-html --cover-html-dir=cover

clean: ## Clean build dist and egg directories left after install
	rm -rf ./dist ./build ./$(PACKAGE).egg-info ./cover
	rm -f MANIFEST
	rm -f ./$(PACKAGE)/*.so
	rm -f ./*_valgrind.log*
	find . -type f -iname '*.pyc' -delete
	find . -type d -name '__pycache__' -empty -delete

develop: ## Install a development version of the package needed for testing
	python setup.py develop --user

dist: ## Make Python source distribution
	python setup.py sdist

docs: doc
doc: install ## Build documentation with Sphinx
	m2r README.md && mv README.rst $(DOC_DIR)
	m2r CHANGELOG.md && mv CHANGELOG.rst $(DOC_DIR)
	$(MAKE) -C $(DOC_DIR) html
