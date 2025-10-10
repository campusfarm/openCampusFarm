#!/bin/bash
# webAPIrun

# Stop on errors
set -Eeuo pipefail
set -x

# Uncomment this command if no virtual environment
# Create a Python virtual environment
# python3 -m venv env

# Uncomment this command if the virtual environment created is not activated
# Activate Python virtual environment
# source env/bin/activate

# Install back end
pip install -r requirements.txt
pip install -e .
