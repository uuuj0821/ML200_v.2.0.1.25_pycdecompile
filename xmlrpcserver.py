# uncompyle6 version 3.5.0
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.5 (default, Nov 16 2020, 22:23:17)
# [GCC 4.8.5 20150623 (Red Hat 4.8.5-44)]
# Embedded file name: /home/dp110/carima/dp110server/xmlrpcserver.py
# Compiled at: 2017-12-26 13:36:21
"""
Created on Jun 19, 2015
info
@author: cloud3
"""
from SimpleXMLRPCServer import SimpleXMLRPCServer, resolve_dotted_attribute
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler
from cls_rpcprintCM import cls_RpcPrintCM
from cls_rpcprintML192 import cls_RpcPrintML192
from cls_rpcprintIM131 import cls_RpcPrint131
import logging, logging.handlers
from logging.handlers import TimedRotatingFileHandler
from ConfigParser import ConfigParser
import os, string, cls_rpcprintIM131
if __name__ == '__main__':
    logger = logging.getLogger('dp110server')
    hdlr = logging.handlers.TimedRotatingFileHandler('./xmlrpc_server.log', when='d', interval=30, backupCount=3)
    formatter = logging.Formatter('%(funcName)s %(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.INFO)

    class RequestHandler(SimpleXMLRPCRequestHandler):
        """
        http://code.activestate.com/recipes/496700-logging-simplexmlrpcserver/
        """

        def do_POST(self):
            clientIP, port = self.client_address
            logger.info('Client IP: %s - Port: %s' % (clientIP, port))
            try:
                data = self.rfile.read(int(self.headers['content-length']))
                if data.find('%') > 5:
                    logger.info('Client request: uploadfile')
                else:
                    logger.info('Client request: \n%s\n' % data)
                response = self.server._marshaled_dispatch(data, getattr(self, '_dispatch', None))
                logger.info('Server response: \n%s\n' % response)
            except:
                self.send_response(500)
                self.end_headers()
            else:
                self.send_response(200)
                self.send_header('Content-type', 'text/xml')
                self.send_header('Content-length', str(len(response)))
                self.end_headers()
                self.wfile.write(response)
                self.wfile.flush()
                self.connection.shutdown(1)

            return

        rpc_paths = ('/RPC2', )


    class MySimpleXMLRPCServer(SimpleXMLRPCServer):

        def _dispatch(self, method, params):
            func = None
            try:
                func = self.funcs[method]
            except KeyError:
                if self.instance is not None:
                    if hasattr(self.instance, '_dispatch'):
                        return self.instance._dispatch(method, params)
                    try:
                        func = resolve_dotted_attribute(self.instance, method, self.allow_dotted_names)
                    except AttributeError:
                        pass

            if func is not None:
                return func(*params)
            else:
                raise Exception('method "%s" is not supported' % method)
                return


    HOST, PORT = ('0.0.0.0', 9090)
    print 'Running XML-RPC server on %s:%d' % (HOST, PORT)
    server = MySimpleXMLRPCServer((HOST, PORT), logRequests=True, requestHandler=RequestHandler, allow_none=True)
    server.register_introspection_functions()
    server.register_instance(cls_RpcPrintML192('LED'))
    server.serve_forever()
    print 'Stop XML-RPC server on %s:%d' % (HOST, PORT)

    # 2021.12.22 (2.0.1.25)