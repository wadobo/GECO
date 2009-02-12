# -*- coding: utf-8 -*-
# gecolib

import random
import string


LOWER, UPPER, DIGITS, PUNCT = (string.lowercase,
                    string.uppercase,
                    string.digits,
                    '.:;,!?{}[]<>=-_()+#@$%&')

#################################
#                               #
# TODO                          #
# * Change master password      #
# * Change password attributes  #
#                               #
#################################

class GecoClient:
    '''
    Provides a simple object to interact with a GECO server.
    '''

    def __init__(self, server, name='', cookie=''):
        self.server = server
        self.cookie = ''
        self.name = ''
        self._name = name

        if cookie:
            self.cookie = cookie
            self.name = self._name

    def auth(self, user, password):
        self.cookie = self.server.auth(user, password)
        if self.cookie:
            self.name = self._name

    def logout(self):
        self.server.logout(self.cookie)
        self.cookie = ''
        self.name = ''

    def register(self, user, password):
        self.server.register(user, password)

    def check_user_name(self, name):
        return self.server.check_user_name(name)

    def set_password(self, name, password, master, args):
        method = cypher_methods[args.get('cypher_method', '')]
        password = method.encrypt(password, master)
        self.server.set_password(self.cookie, name, password, args)

    def set_raw_password(self, name, password, args):
        self.server.set_password(self.cookie, name, password, args)

    def get_password(self, name, master):
        p = self.server.get_password(self.cookie, name)
        method = cypher_methods[p.get('cypher_method', '')]
        p['password'] = method.decrypt(p['password'], master)
        return p
    
    def decrypt_password(self, p, master):
        method = cypher_methods[p.get('cypher_method', '')]
        return method.decrypt(p['password'], master)

    def cookied(self, f):
        def new_funct(*args, **kwargs):
            return f(self.cookie, *args, **kwargs)
        return new_funct

    def __repr__(self):
        auth = '< Authenticated >' if self.cookie else ''
        return '< GecoClient %s %s >' % (self.name, auth)

    def __getattr__(self, attr):
        return self.cookied(self.server.__getattr__(attr))

def get_server_object(method='xmlrpc', **kwargs):
    '''
    Return an object with methods to interact with the server.

    method is the interface to use (xmlrpc, dbus, ...)

    Returned object implements these methods:
        def auth(self, user, password) -> cookie (str)
        def logout(self, cookie)
        def register(self, user, password)
        def unregister(self, cookie)
        def change_password(self, cookie, new_password)
        def check_user_name(self, name) -> bool
        def set_password(self, cookie, name, password, args)
        def del_password(self, cookie, name)
        def get_password(self, cookie, name) -> password
        def get_passwords(self, cookie, args) -> [password]
        def get_all_passwords(self, cookie) -> [password]

        ...
    '''
    # TODO implementar funcionalidad de ficheros de configuración

    if method == 'xmlrpc':
        import xmlrpclib
        # example xmlrpc server: 'https://localhost:443'
        server = xmlrpclib.Server(kwargs['xmlrpc_server'],
                allow_none=1)

        if kwargs.get('cookie', ''):
            return GecoClient(server, name=kwargs['xmlrpc_server'],
                    cookie=kwargs['cookie'])
        else:
            return GecoClient(server, name=kwargs['xmlrpc_server'])

GSO = get_server_object

def generate(size=11, lower=True, upper=True, digits=True,
        punctuation=False):
    '''
    Generate a random password with set of chars selected by params
    and specified size.
    '''

    chars = ''
    selection = [lower, upper, digits, punctuation]
    strings =(LOWER, UPPER, DIGITS, PUNCT)   

    for opt, v in zip(selection, strings):
        if opt:
            chars += v

    return ''.join([random.choice(chars) for _ in xrange(size)])

def is_sorted(alist):
    '''
    alist is a list of ints

    return True if the list is a well sorted list [1,2,3,4]
    return False if the list isn't well sorted [1,3,4] or [1,3,2]...
    '''

    first = alist[0]
    i = 1
    while i < len(alist):
        if first != alist[i] - 1:
            return False
        first = alist[i]
        i += 1
    return True

def strength(password):
    '''
    Check the strength of a password.

    return 0..1
    '''

    strength = -5

    # bad passwords tests (-20 or -15)
    bad_passwords = ('', 'qwerty', 'asdfg', 'zxcvb')
    if password.lower() in bad_passwords:
        return -20
    ord_pass = [ord(i) for i in password]
    inverted_pass = ord_pass[:]
    inverted_pass.reverse()
    if is_sorted(ord_pass) or is_sorted(inverted_pass):
        return -15

    # repeated chars test
    repeated = 1
    for i in range(len(password) - 1):
        if password[i] == password[i + 1]:
            repeated += 1
    strength -= repeated * 10.0 / len(password)

    # len tests (min -10, max 5)
    if len(password) <= 4:
        strength -= 10
    elif len(password) <= 6:
        strength -= 8
    elif len(password) <= 8:
        strength -= 5
    elif len(password) >= 14:
        strength += 5

    # chars tests (max +20)
    for chars_string in LOWER, UPPER, DIGITS, PUNCT:
        for j in chars_string:
            if j in password:
                strength += 5
                break

    return ((strength + 20) / 40.0)

##################################################
# Algoritmos para cifrar y descifrar contraseñas #
##################################################

import slowaes
import base64

import hashlib

# Some crypt utils
def mult(cad, length=16):
    n = len(cad)
    n = length - (n % length)
    return cad + chr(0)*n

def strip(cad):
    index = cad.find(chr(0))
    to_ret = cad[0:index] if index > 0 else cad
    return to_ret

class AES:
    ''' SlowAES method '''
    def __init__(self):
        self.aes = slowaes.AESModeOfOperation()
    def encrypt(self, msg, key):
        ckey, iv = self.key_and_iv(key)
        mode, orig_len, ciph = self.aes.encrypt(msg, self.aes.modeOfOperation["CBC"],
                ckey, self.aes.aes.keySize["SIZE_128"], iv)
        return '#'.join(map(str, ciph))

    def decrypt(self, msg, key):
        msg = map(int, msg.split('#'))
        ckey, iv = self.key_and_iv(key)
        decr = self.aes.decrypt(msg, 256, self.aes.modeOfOperation["CBC"], ckey,
                self.aes.aes.keySize["SIZE_128"], iv)
        return strip(decr)

    def key_and_iv(self, key):
        '''
        Return a 32 size number key and a 16 size iv from a string key
        '''
        hkey = map(ord, hashlib.sha256(key).digest())
        iv = map(ord, hashlib.md5(key).digest())
        
        return hkey, iv

cypher_methods = {
        'AES': AES(),
        '': AES(),
        }
