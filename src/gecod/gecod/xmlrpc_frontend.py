#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Provides a xmlrpc frontend to gecod backend
'''

import backend
import secure_xmlrpc as sxmlrpc

HOST = 'localhost'
PORT = 4343
DATABASE = 'sqlite:///database.sqlite'
KEYFILE='certs/key.pem'
CERTFILE='certs/cert.pem'

def parseconfig(configfile):
    global HOST, PORT, DATABASE, KEYFILE, CERTFILE
    options = open(configfile).readlines()
    for opt in options:
        k, v = opt.split('=')
        k = k.strip()
        v = v.strip()

        if k == 'host':
            HOST = v
        elif k == 'port':
            PORT = int(v)
        elif k == 'database':
            DATABASE = v
        elif k == 'keyfile':
            KEYFILE = v
        elif k == 'certfile':
            CERTFILE = v

class frontend:
    def __init__(self):
        pass

    def auth(self, user, password):
        '''
        Return the cookie.
        '''
        return backend.auth(user, 'password',
                password=password)

    def logout(self, cookie):
        backend.logout(cookie)

    def register(self, user, password):
        backend.register(user, password)

    def unregister(self, cookie):
        backend.unregister(cookie)

    def change_password(self, cookie, new_password):
        backend.change_password(cookie, new_password)

    def check_user_name(self, name):
        return backend.check_user_name(name)

    def set_password(self, cookie, name, password, args):
        '''
        args is a dict with possible keys:
            type, description, account, expiration

            expiration must be an integer (days)
        '''

        backend.set_password(cookie, name, password, **args)

    def del_password(self, cookie, name):
        backend.del_password(cookie, name)
        
    def get_password(self, cookie, name):
        p = backend.get_password(cookie, name)
        return p

    def get_passwords(self, cookie, args):
        '''
        args is a dict with possible keys:
            name, type, updated, expiration, account
        '''

        p = backend.get_passwords_by(cookie, **args)
        return [i for i in p]
    
    def get_all_passwords(self, cookie):
        '''
        Return all passwords of user
        '''

        p = backend.get_all_passwords(cookie)
        return [i for i in p]

    def export(self, cookie):
        '''
        Returns a string with all passwords
        ready to import
        '''

        return backend.export(cookie)

    def restore(self, cookie, data):
        '''
        Restore data from a backup doit with export
        '''

        backend.restore(cookie, data)

def start_server():
    sxmlrpc.EasyServer(HOST, PORT, frontend())

def main(config='gecod-xmlrpc.conf'):
    if len(sys.argv) > 1:
        parseconfig(config)

    backend.DATABASE = DATABASE
    sxmlrpc.KEYFILE = KEYFILE
    sxmlrpc.CERTFILE = CERTFILE

    try:
        start_server()
    except KeyboardInterrupt:
        print "Closing"

if __name__ == '__main__':
    main()
