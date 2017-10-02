#!/bin/bash

# Script to run on every pull request. Verifies that code passes tests and linting before it is merged to master

# still needs a step to generate settings.py file, but that depends on the machine where this code ends up being run
rm -rf env
virtualenv -p python3 env
. env/bin/activate
pip install -r requirements.txt
pylint ledger
py.test tests.py
