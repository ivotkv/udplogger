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

import sys
import time
import socket
import json
import argparse

class Client(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send(self, model, data):
        send_data = json.dumps({'model': model, 'data': data})
        self.socket.sendto(send_data, (self.host, self.port))
        

if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(argument_default=argparse.SUPPRESS)
    arg_parser.description = 'Test client.'
    arg_parser.add_argument('--host', metavar='HOST', default='localhost',
                            help='server host (default: %(default)s)')
    arg_parser.add_argument('--port', metavar='PORT', type=int, required=True,
                            help='server port')

    args = arg_parser.parse_args()

    print "Server address: {0}:{1}".format(args.host, args.port)
    client = Client(args.host, args.port)

    index = 0
    while True:
        msg = "Message {0}".format(index)
        print "Sending to TestLog: '{0}'".format(msg)

        client.send('TestLog', {'data': msg})

        index += 1
        time.sleep(1)
