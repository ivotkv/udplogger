#!/bin/bash

set -e
set -x

cd $(dirname "${BASH_SOURCE[0]}")

PYTHON=${PYTHON:-"python"}
VENV="venv"

# build clean virtualenv
rm -rf $VENV
virtualenv --python=$PYTHON $VENV
source $VENV/bin/activate

# install standard packages
pip install --upgrade pip
pip install ipython
pip install pytest

# install udplogger dependencies
pip install PyYAML 
pip install argparse
pip install "sqlalchemy>=0.9.1"

# install database drivers
pip install psycopg2
