#!/bin/bash

python -m ruff check

python -m mypy --pretty ./src ./tests

python -m ruff format --diff

python -m vulture ./src

python -m unittest discover ./tests -v -p "test_int*"

python -m coverage run -m unittest discover ./tests/ -v -p "test_unit*"

python -m coverage report -m --fail-under=100
