#!/bin/bash
#
# Simple travis deploy script.
#
# This was added because for some reason the inline bash command failed on 
# Windows. See: 
# https://travis-ci.org/alan-turing-institute/CleverCSV/jobs/618669819
#

set -e
set -x

TRAVIS_TAG="$1"
PIP="$2"
PYTHON="$3"

if [[ "${TRAVIS_EVENT_TYPE}" == "pull_request" ]]
then
	echo "Not deploying on pull request build."
	exit 0;
fi

if [[ "${TRAVIS_TAG:-}" =~ ^v[0-9]\.[0-9]\.[0-9]$ ]]
then
	ls -1 wheelhouse
	$PIP install twine
	$PYTHON -m twine upload --verbose --skip-existing wheelhouse/*
else
	echo "Not deploying, git tag doesn't match"
fi
