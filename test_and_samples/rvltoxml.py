#!/usr/bin/python

import zlib
import sys
import getpass
from Crypto.Cipher import AES

#try:
#    DATAFILE = sys.argv[1]
#except:
#    print "usage:"
#    print " ", sys.argv[0], "passwd_file"
#    sys.exit()
#
#PASSWORD = getpass.getpass()
#
#
## read data from file
#f = open(DATAFILE, "rb")
#data = f.read()
#f.close()
#
#
## pad the password
#PASSWORD += (chr(0) * (32 - len(PASSWORD)))
#
## get the IV
#c = AES.new(PASSWORD)
#iv = c.decrypt(data[12:28])
#
## decrypt the data
#c = AES.new(PASSWORD, AES.MODE_CBC, iv)
#rawdata = c.decrypt(data[28:])
#
## fetch padlen, and decompress data
#padlen = ord(rawdata[-1])
#xmldata = zlib.decompress(rawdata[:-padlen], 15, 32768)
#
#
## print xml data
#print xmldata

def encrypt(msg, passwd):
    # pad the password
    passwd += (chr(0) * (32 - len(passwd)))
    msg += (chr(0) * (32 - len(msg)))

    # get the IV
    c = AES.new(passwd)
    msg_c = c.encrypt(msg)
    import base64
    print base64.encodestring(msg_c)

def decrypt(msg, passwd):
    # pad the password
    passwd += (chr(0) * (32 - len(passwd)))

    import base64
    msg = base64.decodestring(msg)

    # get the IV
    c = AES.new(passwd)
    iv = c.decrypt(msg[12:28])

    # decrypt the data
    c = AES.new(passwd, AES.MODE_CBC, iv)
    rawdata = c.decrypt(msg)

#    # fetch padlen, and decompress data
#    padlen = ord(rawdata[-1])
#    msg_d = zlib.decompress(rawdata[:-padlen], 15, 32768)


    print base64.decodestring(rawdata)
