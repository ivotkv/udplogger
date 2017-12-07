#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# The MIT License (MIT)
# 
# Copyright (c) 2016 Ivo Tzvetkov
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
# 

from __future__ import print_function, unicode_literals
import yaml
import argparse
import json
import httpagentparser
from datetime import datetime
from hashlib import md5
from tornado.web import RequestHandler, Application
from tornado.ioloop import IOLoop
try:
    from .client import Client
except ValueError:
    from client import Client

class NotPermitted(Exception):
    pass

class MainHandler(RequestHandler):

    def initialize(self, host, port, default_table, force_default_table=False,
                   include_request_info=False, enforce_token=False,
                   token_data=None, token_salt=None):
        self.udp = Client(host, port)
        self.default_table = default_table
        self.force_default_table = force_default_table
        self.include_request_info = include_request_info
        self.enforce_token = enforce_token
        self.token_data = token_data
        self.token_salt = token_salt

    def get(self):
        try:
            if self.force_default_table or 't' not in self.request.arguments:
                table = self.default_table
            else:
                table = self.get_argument('t')
            data = json.loads(self.get_argument('d'))
            if self.enforce_token:
                token = md5(':'.join([
                            self.token_salt,
                            self.request.headers.get('User-Agent', ''),
                            data.get(self.token_data, '')
                        ]).encode('utf-8')).hexdigest()
                if data['token'] != token:
                    raise NotPermitted('invalid token')
                del data['token']
            if self.include_request_info:
                data['date'] = str(datetime.now())
                data['host'] = self.request.host
                data['remote_ip'] = self.request.remote_ip
                data['agent_string'] = self.request.headers.get('User-Agent', '')
                agent_info = httpagentparser.simple_detect(data['agent_string'])
                data.update(zip(('agent_os', 'agent_browser'), agent_info))
            self.udp.send(table=table, data=data)
        except Exception as e:
            print("{0}: {1}: {2}".format(e.__class__.__name__, e, self.request.arguments))

        # Return a 1x1 GIF with appropriate headers
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.set_header('Pragma', 'no-cache')
        self.set_header('X-Content-Type-Options', 'nosniff')
        self.set_header('Content-Type', 'image/gif')
        self.write('GIF89a\x01\x00\x01\x00\x80\xff\x00\xff\xff\xff\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;')

def run():
    arg_parser = argparse.ArgumentParser()
    arg_parser.description = 'A simple web server to forward data to UDPLogger.'
    arg_parser.add_argument('-c', '--config', metavar='FILE',
                            default='config.yaml',
                            help='path to config file (default: %(default)s)')
    args = arg_parser.parse_args()

    with open(args.config, 'r') as file:
        config = yaml.load(file)

    app = Application([
        (r".*", MainHandler, {
            'host': config['server']['host'],
            'port': config['server']['port'],
            'default_table': config['web']['default_table'],
            'force_default_table': config['web']['force_default_table'],
            'include_request_info': config['web']['include_request_info'],
            'enforce_token': config['web']['token']['enforce'],
            'token_data': config['web']['token']['data'],
            'token_salt': config['web']['token']['salt']
        })
    ])
    app.listen(config['web']['port'], xheaders=True)

    print("Server listening on port {0}".format(config['web']['port']))
    IOLoop.current().start()

if __name__ == "__main__":
    run()
