#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Provides a xmlrpc frontend to gecod backend
'''

import backend
import secure_xmlrpc as sxmlrpc

HOST = 'localhost'
PORT = 4343

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

    def check_user_name(self, name):
        return backend.check_user_name(name)

    def set_password(self, cooke, name, password, args):
        '''
        args is a dict with possible keys:
            type, description, account, expiration
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
        return p

def start_server():
    sxmlrpc.EasyServer(HOST, PORT, frontend())

if __name__ == '__main__':
    try:
        start_server()
    except KeyboardInterrupt:
        print "Closing"
