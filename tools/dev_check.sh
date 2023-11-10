#!/bin/bash

set -e

python -m pylint ./src/gridfinity_build123d/ ./tests/

python -m flake8 --count --show-source --statistics ./src ./tests

python -m mypy --pretty ./src ./tests

python -m vulture ./src

python -m black --check --diff --color ./src ./tests

python -m darglint src/

python -m unittest discover ./tests -v -p "test_int*"

python -m coverage run -m unittest discover ./tests/ -v -p "test_unit*"

python -m coverage report -m --fail-under=100