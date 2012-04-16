#!/usr/bin/env python

import urllib
import httplib
import json

BASE = 'localhost:8080'

def request(path, **params):
    data = urllib.urlencode(params)

    h = httplib.HTTPConnection(BASE)

    h.request('POST', "/%s" % path, data)

    r = h.getresponse()
    return json.loads(r.read())


# registering
request('register', user='danigm', password="123")
# login
response = request('auth', user='danigm', password='123')
cookie = response['data']

#data = "pw2|ssh|pw2|root|pw2||1334598426.0|1364838440.0\npw1|web|pw1|danigm|pw1||1334598440.0|1334857640.0"
#request('restore', cookie=cookie, data=data)

print urllib.urlencode({'cookie':cookie})
# adding password
args = json.dumps(dict(type="web", description="pw1", account="danigm", expiration=3))
request('set_password', cookie=cookie, name='pw1', password='pw1', args=args)
args = json.dumps(dict(type="ssh", description="pw2", account="root", expiration=350))
request('set_password', cookie=cookie, name='pw2', password='pw2', args=args)
# getting password list
print [i['name'] for i in request('get_all_passwords', cookie=cookie)['data']]
# removing password 2
remove = True
while remove:
    request('del_password', cookie=cookie, name='pw2')
    response = request('get_password', cookie=cookie, name='pw2')
    if response['status'] == "error":
        remove = False

# getting password 1
response = request('get_password', cookie=cookie, name='pw1')
print response['data']

# modifying password 1
args = json.dumps(dict(type="ssh", password='pw2', description="pw2", account="root", expiration=350))
response = request('change_attr', cookie=cookie, name='pw1', args=args)

# getting password 1
response = request('get_password', cookie=cookie, name='pw1')
print response['data']

remove = True
while remove:
    response = request('del_password', cookie=cookie, name='pw1')
    if response['status'] == "error":
        remove = False

# unregistering
request('unregister', cookie=cookie)
