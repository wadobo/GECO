#!/usr/bin/python
# -*- coding: utf-8 -*-
# TODO cifrar/descifrar passwords

'''
Terminal GECO client
'''

import gecolib
import sys
import os
import getopt
import types
import getpass

def _parse_user_hostname(args, options='u:h:'):
    username = os.environ['USER']
    hostname = 'https://localhost:4343'

    opts, others = getopt.getopt(args, options)
    for opt, value in opts:
        if opt == '-u':
            username = value
        elif opt == '-h':
            hostname = value
    
    if not username:
        username = os.environ['USER']

    return username, hostname

def list(args):
    ''' Lista todas las contraseñas
        opciones:
        -u username
        -h host (https://localhost:4343)
    '''
    
    username, hostname = _parse_user_hostname(args)
    password = getpass.getpass()
    try:
        server = gecolib.get_server_object(xmlrpc_server=hostname)
        cookie = server.auth(username, password)
        passwords = server.get_all_passwords(cookie)
        server.logout(cookie)
    except:
        print "No se ha podido autenticar %s, %s" % (username,
                hostname)
        sys.exit()
                
    for p in passwords:
        print '%-10s %-20s %-10s' % (p['name'], p['account'],
                p['type'])

def pwd(args):
    ''' Devuelve una contraseña en concreto
        opciones:
        -u username
        -h host (https://localhost:4343)
        -n name
    '''

    options = 'u:h:n:'
    username, hostname = _parse_user_hostname(args, options)
    password = getpass.getpass()

    passname = ''
    opts, others = getopt.getopt(args, options)
    for opt, value in opts:
        if opt == '-n':
            passname = value

    try:
        server = gecolib.get_server_object(xmlrpc_server=hostname)
        cookie = server.auth(username, password)
    except:
        print "No se ha podido autenticar %s, %s" % (username,
                hostname)
        sys.exit()

    try:
        password = server.get_password(cookie, passname)
        server.logout(cookie)
    except:
        print "Password no encontrado %s" % passname
        sys.exit()

    print "'%s'" % password['password']

def setpwd(args):
    ''' Almacena un password en el servidor
        opciones:
        -u username
        -h host (https://localhost:4343)
        -n name

        opcionales:
        -r random password
        -p password
        -t tipo (generic, web, email, unix)
        -d descripcion
        -a cuenta
        -x tiempo de expiración en días (60 por defecto)
    '''

    options = 'u:h:n:t:d:a:x:p:r'
    username, hostname = _parse_user_hostname(args, options)
    password = getpass.getpass()

    passname = ''
    key_args = {}
    opts, others = getopt.getopt(args, options)
    for opt, value in opts:
        if opt == '-n':
            passname = value
        elif opt == '-t':
            key_args['type'] = value
        elif opt == '-d':
            key_args['description'] = value
        elif opt == '-a':
            key_args['account'] = value
        elif opt == '-x':
            key_args['expired'] = int(value)
        elif opt == '-p':
            real_password = value
        elif opt == '-r':
            real_password = gecolib.generate()

    try:
        server = gecolib.get_server_object(xmlrpc_server=hostname)
        cookie = server.auth(username, password)
    except:
        print "No se ha podido autenticar %s, %s" % (username,
                hostname)
        sys.exit()

    server.set_password(cookie, passname, real_password, key_args)

    server.logout(cookie)

def help(args):
    ''' Muestra esta ayuda '''
    print help_str

# Muestra todas las funciones como opciones
help_str = '''
Modo de empleo:
    %s opciones

opciones:
''' % sys.argv[0]

functions = [v for v in globals().values()\
        if type(v) == types.FunctionType\
        if not v.__name__.startswith('_')]
function_names = [v.__name__ for v in functions]
callable_functions = dict(zip(function_names, functions))

# Componiendo la ayuda de las funciones a partir de la documentación
for function in functions:
    help_str += '    "%(opt)s" %(desc)s\n' %\
            {'opt': function.__name__,
             'desc': function.__doc__}

if __name__ == '__main__':
    args = sys.argv[1:]

    if len(args) < 1:
        help([])
    elif not args[0] in function_names:
        help([])
    else:
        callable_functions[args[0]](args[1:])
