import py_compile
import os
py_compile.compile(os.environ.get('HOME','/home/dp110')+'/carima/dp110server/xmlrpcserver.py')