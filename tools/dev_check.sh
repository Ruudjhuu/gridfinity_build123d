#!/bin/bash

set -e

python -m pylint ./src/gridfinity_build123d/ ./tests/

python -m flake8 --count --show-source --statistics ./src ./tests

python -m mypy --pretty ./src ./tests

python -m black --check --diff --color ./src ./tests

python -m coverage run -m unittest discover ./tests/ -v

python -m coverage report -m --fail-under=100