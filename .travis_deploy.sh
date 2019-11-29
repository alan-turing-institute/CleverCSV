#!/bin/bash
#
# Simple travis deploy script

set -e
set -x

TRAVIS_TAG="$1"
PIP="$2"
PYTHON="$3"

if [[ "${TRAVIS_TAG:-}" =~ ^v[0-9]\.[0-9]\.[0-9]$ ]]
then
	ls -1 wheelhouse
	$PIP install twine
	$PYTHON -m twine upload --verbose --skip-existing wheelhouse/*
else
	echo "Not deploying, git tag doesn't match"
fi
