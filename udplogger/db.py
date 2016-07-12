# -*- coding: utf-8 -*-
# 
# The MIT License (MIT)
# 
# Copyright (c) 2016 Ivaylo Tzvetkov, ChallengeU
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
# 

import re
import os
import glob
import sqlalchemy
import elixir
from elixir import Entity
from imp import load_source

# Configure Elixir
elixir.session.configure(autoflush=False)

elixir.options_defaults.update(dict(
    tablename = lambda cls: cls.__name__.lower(),
    inheritance = 'concrete',
    polymorphic = False
))

# Model loading
model_map = {}

class ModelNotFound(Exception): pass

def add_model(model):
    global model_map
    model_map[model.__name__] = model

def get_model(model_name, log_errors=True):
    global model_map
    try:
        return model_map[model_name]
    except KeyError:
        raise ModelNotFound("Model not found: '{0}'".format(model_name))

# Initialize the db
def init(config):
    # Connect to database
    dburl = "{0}://{1}:{2}@{3}/{4}".format(config['type'],
                                           config['user'],
                                           config['pass'],
                                           config['host'],
                                           config['name'])

    elixir.metadata.bind = sqlalchemy.create_engine(dburl, pool_recycle=3600)

    # Load base models
    from udplogger.models import BaseLog, ErrorLog
    add_model(BaseLog)
    add_model(ErrorLog)

    # Load user-defined models
    load_source("usermodels", os.path.join(config['model_path'], '__init__.py'))
    for fname in glob.glob(os.path.join(config['model_path'], '[a-zA-Z]*.py')):
        module_name = "usermodels.{0}".format(re.sub(r'^.*/([^/]+).py$', r'\1',
                                                     fname))
        module = load_source(module_name, fname)
        for key in module.__dict__:
            value = getattr(module, key)
            if (value is not Entity and isinstance(value, type) and
                issubclass(value, Entity)):
                add_model(value)

    # Setup Elixir, create tables as needed
    elixir.setup_all(True)
