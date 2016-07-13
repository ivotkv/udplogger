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
import json
import yaml
import argparse
import signal
import threading
from SocketServer import UDPServer, ThreadingMixIn, BaseRequestHandler
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.ext.declarative.api import DeclarativeMeta
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import create_engine


signals = {signal.SIGTERM: 'SIGTERM',
           signal.SIGINT: 'SIGINT',
           signal.SIGHUP: 'SIGHUP'}

threading.stack_size(256 * 1024)

class InvalidTableName(Exception):
    pass

class TableNotFound(Exception):
    pass

class Database(object):

    def __init__(self, config):
        self.url = "{0}://{1}:{2}@{3}/{4}".format(config['type'],
                                                  config['user'],
                                                  config['pass'],
                                                  config['host'],
                                                  config['name'])
        self.engine = create_engine(self.url, pool_recycle=3600)
        self.automap = automap_base()
        self.automap.prepare(self.engine, reflect=True)
        self.sessionmaker = sessionmaker(bind=self.engine, autoflush=False)

    def session(self):
        return self.sessionmaker()

    def table(self, name):
        table = getattr(self.automap.classes, name.lower(), None)
        if table is not None and not isinstance(table, DeclarativeMeta):
            raise InvalidTableName(u"'{0}' is a reserved name and cannot be a table name".format(name))
        return table


class RequestHandler(BaseRequestHandler):

    database = None

    def handle(self):
        session = self.database.session()

        src_ip = self.client_address[0]
        raw_data = self.request[0].strip()

        try:
            data = json.loads(raw_data)
            table = self.database.table(data['table'])
            if table is None:
                raise TableNotFound(u"'{0}' does not exist or is not a viable SQLAlchemy table".format(data['table']))
            if isinstance(getattr(table, 'src_ip', None), InstrumentedAttribute):
                data['data']['src_ip'] = src_ip
            session.add(table(**data['data']))
        except Exception as e:
            error = self.database.table('udplogger_errors')
            if error is not None:
                entry = session.add(error(src_ip=src_ip,
                                          error=e.__class__.__name__,
                                          description=unicode(e),
                                          data=raw_data))
            else:
                sys.stderr.write(u"{0}: {1}: {2}\n".format(e.__class__.__name__, e, raw_data).encode('utf-8'))

        try:
            session.commit()
        except SQLAlchemyError as e:
            sys.stderr.write(u"{0}: {1}: {2}\n".format(e.__class__.__name__, e, raw_data).encode('utf-8'))
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
        RequestHandler.database = Database(self.config['database'])

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
    arg_parser = argparse.ArgumentParser()
    arg_parser.description = 'UDP logging server.'
    arg_parser.add_argument('-c', '--config', metavar='FILE',
                            default='config.yaml',
                            help='path to config file (default: %(default)s)')
    args = arg_parser.parse_args()

    server = Server(args.config)
    server.start()


if __name__ == "__main__":
    run()
