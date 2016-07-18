#!/usr/bin/env python
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

import yaml
import argparse
import simplejson as json
import tornado.ioloop
import tornado.web
from client import Client


class MainHandler(tornado.web.RequestHandler):

    def initialize(self, host, port):
        self.udp = Client(host, port)

    def get(self):
        try:
            self.udp.send(table=self.get_argument('table'),
                          data=json.loads(self.get_argument('data')))
            self.write('OK')
        except Exception as e:
            print u"{0}: {1}: {2}".format(e.__class__.__name__, e, self.request.arguments)
            self.write('ERR')


def run():
    arg_parser = argparse.ArgumentParser()
    arg_parser.description = 'A simple web server to forward data to UDPLogger.'
    arg_parser.add_argument('-c', '--config', metavar='FILE',
                            default='config.yaml',
                            help='path to config file (default: %(default)s)')
    args = arg_parser.parse_args()

    config = yaml.load(file(args.config, 'r'))

    app = tornado.web.Application([
        (r".*", MainHandler, {
            'host': config['server']['host'],
            'port': config['server']['port']
        })
    ])
    app.listen(config['web']['port'])

    print "Server listening on port {0}".format(config['web']['port'])
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    run()
