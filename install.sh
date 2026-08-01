#!/bin/bash

# These will be managed entirely with pip soon,
# but I may need to work on yt for a bit

git submodule update --recursive --init

# yt for new plotting
cd external/yt
pip install -e .
cd ../..

# Library and set management
cd external/hallmark
pip install -e .
cd ../..

# Install pyharm
pip install -e .
