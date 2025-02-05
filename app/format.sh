#!/bin/sh
set -e

echo "Running autoflake..."
autoflake --in-place --recursive --remove-all-unused-imports --ignore-init-module-imports .

echo "Running yapf..."
yapf --in-place --recursive --style=pep8 .

echo "Running isort..."
isort .

echo "Code formatting complete."
