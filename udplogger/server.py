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

import os
import sys
import signal
import socket
import threading
from SocketServer import UDPServer, ThreadingMixIn, BaseRequestHandler
from sqlalchemy.exc import SQLAlchemyError
from elixir import session
import db
import json
import yaml
import argparse

signals = {signal.SIGTERM: 'SIGTERM',
           signal.SIGINT: 'SIGINT',
           signal.SIGHUP: 'SIGHUP'}

threading.stack_size(256 * 1024)


class RequestHandler(BaseRequestHandler):

    def handle(self):
        session.close()

        src_ip = self.client_address[0]
        raw_data = self.request[0].strip()

        try:
            data = json.loads(raw_data)
            model = db.get_model(data['model'])
            entry = model(src_ip = src_ip, **data['data'])
        except Exception as e:
            ErrorLog = db.get_model('ErrorLog')
            entry = ErrorLog(src_ip = src_ip,
                             error = e.__class__.__name__,
                             description = str(e),
                             data = raw_data)

        try:
            session.commit()
        except SQLAlchemyError as e:
            sys.stderr.write("Failed to commit data from {0}: '{1}'\nException: {2}\n".format(src_ip, raw_data, e))
            session.rollback()


class ThreadedUDPServer(ThreadingMixIn, UDPServer):
    pass


class Server(object):
    def __init__(self, config):
        if isinstance(config, basestring):
            config = yaml.load(file(config, 'r'))
        self.config = config
        self.host = self.config['server']['host']
        self.port = self.config['server']['port']
        self.server = None

        # Set up signal handling
        for signum in signals.keys():
            signal.signal(signum, self.sighandler)

    def sighandler(self, signum, frame):
        print "Active threads: {0}".format(threading.active_count())
        print "Received {0}, exiting!".format(signals[signum])
        if self.server:
            self.server.shutdown()
        sys.exit(-signum)

    def start(self):
        # Set up the db
        db.init(self.config['database'])

        # Set up the server
        self.server = ThreadedUDPServer((self.host, self.port), RequestHandler)
        self.server.request_queue_size = 50

        # Get actual host and port
        self.host, self.port = self.server.server_address

        # Start server thread (which will start a thread for each request)
        server_thread = threading.Thread(target=self.server.serve_forever)
        server_thread.daemon = True
        server_thread.start()

        print "Server listening on {0}:{1}".format(self.host, self.port)
        while True:
            # TODO emit stats to graphite (thread count, etc...)
            signal.pause()


def run():
    arg_parser = argparse.ArgumentParser(argument_default=argparse.SUPPRESS)
    arg_parser.description = 'UDP logging server.'
    arg_parser.add_argument('--config', metavar='FILE',
                            default='/etc/udplogger/config.yaml',
                            help='path to config file (default: %(default)s)')

    args = arg_parser.parse_args()

    server = Server(args.config)
    server.start()


if __name__ == "__main__":
    run()
