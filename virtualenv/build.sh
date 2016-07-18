#!/bin/bash

set -e
set -x

cd $(dirname "${BASH_SOURCE[0]}")

PYTHON_VERSION=${PYTHON_VERSION:-"2.7"}

DIRNAME="python-$PYTHON_VERSION"

# build clean virtualenv
rm -rf $DIRNAME
virtualenv --python=python$PYTHON_VERSION $DIRNAME
source $DIRNAME/bin/activate

# install standard packages
pip install --upgrade pip
pip install ipython
pip install pytest

# install udplogger dependencies
pip install PyYAML 
pip install argparse
pip install simplejson
pip install "sqlalchemy>=0.9.1"
pip install tornado

# install database drivers
pip install MySQL-python

# symlink udplogger into virtualenv for convenience
ln -s ../../../../../udplogger $DIRNAME/lib/python$PYTHON_VERSION/site-packages/
