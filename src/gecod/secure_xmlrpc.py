# -*- coding: utf-8 -*-

"""
SecureXMLRPCServer.py - simple XML RPC server supporting SSL.

Based on this article: http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/81549

For windows users: http://webcleaner.sourceforge.net/pyOpenSSL-0.6.win32-py2.4.exe

code copied from http://code.activestate.com/recipes/496786/
"""

# Configure below
LISTEN_HOST='127.0.0.1' # You should not use '' here, unless you have a real FQDN.
LISTEN_PORT=443

KEYFILE='certs/key.pem'    # Replace with your PEM formatted key file
CERTFILE='certs/cert.pem'  # Replace with your PEM formatted certificate file
# Configure above

import SocketServer
import BaseHTTPServer
import SimpleHTTPServer
import SimpleXMLRPCServer

import socket, os
from OpenSSL import SSL

class SecureXMLRPCServer(BaseHTTPServer.HTTPServer, SimpleXMLRPCServer.SimpleXMLRPCDispatcher):
    def __init__(self, server_address, HandlerClass, logRequests=True):
        """Secure XML-RPC server.

        It it very similar to SimpleXMLRPCServer but it uses HTTPS for transporting XML data.
        """
        self.logRequests = logRequests

        SimpleXMLRPCServer.SimpleXMLRPCDispatcher.__init__(self,
                False, None)
        SocketServer.BaseServer.__init__(self, server_address, HandlerClass)
        ctx = SSL.Context(SSL.SSLv23_METHOD)
        ctx.use_privatekey_file (KEYFILE)
        ctx.use_certificate_file(CERTFILE)
        self.socket = SSL.Connection(ctx, socket.socket(self.address_family,
                                                        self.socket_type))
        self.server_bind()
        self.server_activate()

class SecureXMLRPCRequestHandler(SimpleXMLRPCServer.SimpleXMLRPCRequestHandler):
    """Secure XML-RPC request handler class.

    It it very similar to SimpleXMLRPCRequestHandler but it uses HTTPS for transporting XML data.
    """
    def setup(self):
        self.connection = self.request
        self.rfile = socket._fileobject(self.request, "rb", self.rbufsize)
        self.wfile = socket._fileobject(self.request, "wb", self.wbufsize)
        
    def do_POST(self):
        """Handles the HTTPS POST request.

        It was copied out from SimpleXMLRPCServer.py and modified to shutdown the socket cleanly.
        """

        try:
            # get arguments
            data = self.rfile.read(int(self.headers["content-length"]))
            # In previous versions of SimpleXMLRPCServer, _dispatch
            # could be overridden in this class, instead of in
            # SimpleXMLRPCDispatcher. To maintain backwards compatibility,
            # check to see if a subclass implements _dispatch and dispatch
            # using that method if present.
            response = self.server._marshaled_dispatch(
                    data, getattr(self, '_dispatch', None)
                )
        except: # This should only happen if the module is buggy
            # internal error, report as HTTP server error
            self.send_response(500)
            self.end_headers()
        else:
            # got a valid XML RPC response
            self.send_response(200)
            self.send_header("Content-type", "text/xml")
            self.send_header("Content-length", str(len(response)))
            self.end_headers()
            self.wfile.write(response)

            # shut down the connection
            self.wfile.flush()
            self.connection.shutdown() # Modified here!
    
def test(HandlerClass=SecureXMLRPCRequestHandler, ServerClass=SecureXMLRPCServer):
    """Test xml rpc over https server"""
    class xmlrpc_registers:
        def __init__(self):
            import string
            self.python_string = string
            
        def add(self, x, y):
            return x + y
    
        def mult(self, x, y):
            return x * y
    
        def div(self, x, y):
            return x // y
        
    server_address = (LISTEN_HOST, LISTEN_PORT) # (address, port)
    server = ServerClass(server_address, HandlerClass)    
    server.register_instance(xmlrpc_registers())    
    sa = server.socket.getsockname()
    print "Serving HTTPS on", sa[0], "port", sa[1]
    server.serve_forever()

# code by danigm
class EasyServer:
    def __init__(self, host, port, to_serve=None):
        self.host = host
        self.port = port

        if to_serve:
            self.serve(to_serve)

    def serve(self, to_serve):
        '''
        to_serve is an object with exported functions as methods
        '''
        server_address = (self.host, self.port)
        server = SecureXMLRPCServer(server_address, SecureXMLRPCRequestHandler)
        server.register_instance(to_serve)    
        sa = server.socket.getsockname()
        print "Serving HTTPS on", sa[0], "port", sa[1]
        server.serve_forever()

def test2():
    class xmlrpc_registers:
        def __init__(self):
            import string
            self.python_string = string
            
        def add(self, x, y):
            return x + y
    
        def mult(self, x, y):
            return x * y
    
        def div(self, x, y):
            return x // y

    EasyServer(LISTEN_HOST, LISTEN_PORT, xmlrpc_registers())

if __name__ == '__main__':
    #test()
    test2()


# Here is the client for testing:
#import xmlrpclib
#
#server = xmlrpclib.Server('https://localhost:443')
#print server.add(1,2)
#print server.div(10,4)
