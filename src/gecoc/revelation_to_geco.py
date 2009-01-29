#!/usr/bin/python
# -*- coding: utf-8 -*-

import zlib
import sys
import getpass
from Crypto.Cipher import AES
import gecolib
from xml.dom import minidom

try:
    DATAFILE = sys.argv[1]
except:
    print "usage:"
    print " ", sys.argv[0], "passwd_file"
    sys.exit()

SERVER = raw_input('servidor (user@http://server:port): ')
USER, SERVER = SERVER.split('@')
USER_PWD = getpass.getpass('Contraseña de login: ')
PASSWORD = getpass.getpass('Contraseña del fichero rvl: ')


# read data from file
f = open(DATAFILE, "rb")
data = f.read()
f.close()


# pad the password
PASSWORD += (chr(0) * (32 - len(PASSWORD)))

# get the IV
c = AES.new(PASSWORD)
iv = c.decrypt(data[12:28])

# decrypt the data
c = AES.new(PASSWORD, AES.MODE_CBC, iv)
rawdata = c.decrypt(data[28:])

# fetch padlen, and decompress data
padlen = ord(rawdata[-1])
xmldata = zlib.decompress(rawdata[:-padlen], 15, 32768)


# print xml data
#print xmldata

gso = gecolib.GSO(xmlrpc_server=SERVER)
gso.auth(USER, USER_PWD)

master = getpass.getpass('Contraseña maestra: ')

dom = minidom.parseString(xmldata)
for password in dom.getElementsByTagName("entry"):
    type = password.attributes['type'].value
    name = password.getElementsByTagName('name')[0].firstChild.nodeValue.replace(' ', '_')
    description = password.getElementsByTagName('description')[0].firstChild
    description = description.nodeValue if description else ''
    fields = password.getElementsByTagName('field')
    for f in fields:
        if f.attributes['id'].value == 'generic-password':
            pwd = f.firstChild.nodeValue
    
    args = dict(type=type, description=description)
    
    gso.set_password(name, pwd, master, args)
    
