#!/usr/bin/python2

import urllib
import urllib2
import json


url_base = 'http://localhost:8082/'

# Registro
values = {'user' : 'prueba' , 'password' : 'qwerty'}

data = urllib.urlencode(values)
req = urllib2.Request(url_base+'register', data)
rep = urllib2.urlopen(req)
rep_str = rep.read()

print rep_str

# Auth
values = {'user' : 'prueba' , 'password' : 'qwerty'}

data = urllib.urlencode(values)
req = urllib2.Request(url_base+'auth', data)
rep = urllib2.urlopen(req)
rep_str = rep.read()

print rep_str

dic = json.loads(rep_str)
cookie = dic['cookie']

# Add password
values = {'cookie' : cookie, 'name' : 'google', 'password' : 'qwerty'}

data = urllib.urlencode(values)
req = urllib2.Request(url_base+'set_password', data)
rep = urllib2.urlopen(req)
rep_str = rep.read()

print rep_str

# Get all passwords
values = {'cookie' : cookie}

data = urllib.urlencode(values)
req = urllib2.Request(url_base+'get_all_passwords', data)
rep = urllib2.urlopen(req)
rep_str = rep.read()

print rep_str

# Unregister
values = {'cookie' : cookie}

data = urllib.urlencode(values)
req = urllib2.Request(url_base+'unregister', data)
rep = urllib2.urlopen(req)
rep_str = rep.read()

print rep_str
