#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
if sys.version_info[0] < 3:
    from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
else:
    from http.server import BaseHTTPRequestHandler, HTTPServer

import traceback
import threading
import resource
import json
import time
import ssl
import cgi
from _core.router import Router
from _core.http_handler import Http_Handler
from _core.log import Log

# Settings
#
HOST_NAME = '0.0.0.0'
PORT_NUMBER = 5000 # change below 1024 will need sudo permission

# For https configuration
# SSL_CERTIFICATE_FILE='{PATH}/key.pem'
# SSL_CERTIFICATE_KEY_FILE='{PATH}/certificate.pem'
#
SSL_CERTIFICATE_PUBLIC_KEY_FILE = ''
SSL_CERTIFICATE_PRIVATE_KEY_FILE = ''

# Reference from
# https://stackoverflow.com/questions/19537132
#
import socket
import errno
class ThreadedHTTPServer(HTTPServer):
    def process_request(self, request, client_address):
        thread = threading.Thread(target=self.__new_request, args=(self.RequestHandlerClass, request, client_address, self))
        thread.start()
    def __new_request(self, handlerClass, request, address, server):
        try:
            handlerClass(request, address, server)
            self.shutdown_request(request)
        except socket.error as e:
            if e.errno != errno.EPIPE:
                raise
            Log.l("Client disconnected ...")
            Log.l(traceback.extract_stack())
            Log.l(e)
            pass

# Main
#
if __name__ == '__main__':

    server_class = ThreadedHTTPServer
    httpd = server_class((HOST_NAME, PORT_NUMBER), Http_Handler)
    httpd.allow_reuse_address = True
    if SSL_CERTIFICATE_PUBLIC_KEY_FILE != '' and SSL_CERTIFICATE_PRIVATE_KEY_FILE != '' :
        httpd.socket = ssl.wrap_socket(httpd.socket, keyfile=SSL_CERTIFICATE_PUBLIC_KEY_FILE,
                                        certfile=SSL_CERTIFICATE_PRIVATE_KEY_FILE, server_side=True)

    Log.l("[SERVER][%s][SERVER_START][%s][%s]" % (time.asctime(), HOST_NAME, PORT_NUMBER))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    except Exception:
        pass

    httpd.server_close()
    Log.l("[SERVER][%s][SERVER_STOP][%s][%s]" % (time.asctime(), HOST_NAME, PORT_NUMBER))
    exit()
