#!/usr/bin/python

import web
import json
import backend

urls = (
        '/auth', 'auth',
        '/logout', 'logout',
        '/register', 'register',
        '/unregister', 'unregister',
        '/change_password', 'change_password',
        '/change_attr', 'change_attr',
        '/check_user_name', 'check_user_name',
        '/set_password', 'set_password',
        '/del_password', 'del_password',
        '/get_password', 'get_password',
        '/get_passwords', 'get_passwords',
        '/get_all_passwords', 'get_all_passwords',
        '/export', 'export',
        '/restore', 'restore',
        )

app = web.application(urls, globals())


class auth:
    def POST(self):
        '''
        Return the cookie.
        '''
        inp = web.input()
        cookie = backend.auth(inp.user, 'password', password=inp.password)
        if cookie:
            return json.dumps({'status' : 'ok', 'cookie' : cookie})
        return json.dumps({'status' : 'error'})

class logout:
    def POST(self):
        inp = web.input()
        backend.logout(inp.cookie)
        return json.dumps({'status' : 'ok'})

class register:
    def POST(self):
        inp = web.input()
        try:
            backend.register(inp.user, inp.password)
        except:
            return json.dumps({'status' : 'error'})
        return json.dumps({'status' : 'ok'})

class unregister:
    def POST(self):
        inp = web.input()
        backend.unregister(inp.cookie)
        return json.dumps({'status' : 'ok'})

class change_password:
    def POST(self):
        inp = web.input()
        backend.change_password(inp.cookie, inp.new_password)
        return json.dumps({'status' : 'ok'})

class change_attr:
    def POST(self):
        '''
        args is a dict with possible keys:
            type, description, account, expiration, password

            expiration must be a datetime
        '''
        inp = web.input()
        cookie = inp.pop('cookie')
        name = inp.pop('name')
        backend.change_attr(cookie, name, **inp)
        return json.dumps({'status' : 'ok'})


class check_user_name:
    def POST(self):
        inp = web.input()
        result = backend.check_user_name(inp.name)
        return json.dumps({'status' : result})

class set_password:
    def POST(self):
        '''
        args is a dict with possible keys:
            type, description, account, expiration

            expiration must be an integer (days)
        '''

        inp = web.input()
        cookie = inp.pop('cookie')
        name = inp.pop('name')
        password = inp.pop('password')
        backend.set_password(cookie, name, password, **inp)
        return json.dumps({'status' : 'ok'})

class del_password:
    def POST(self):
        inp = web.input()
        backend.del_password(inp.cookie, inp.name)
        return json.dumps({'status' : 'ok'})

class get_password: 
    def POST(self):
        inp = web.input()
        p = backend.get_password(inp.cookie, inp.name)
        return json.dumps({'status' : 'ok', 'password' : p.serialize()})

class get_passwords:
    def POST(self):
        inp = web.input()
        cookie = inp.pop('cookie')
        p = backend.get_passwords_by(cookie, **inp)
        return json.dumps({'status' : 'ok', 'passwords' :
            [i.serialize() for i in p]})

class get_all_passwords: 
    def POST(self):
        '''
        Return all passwords of user
        '''
        inp = web.input()
        p = backend.get_all_passwords(inp.cookie, from_db=True)
        return json.dumps({'status' : 'ok', 'passwords' :
            [i.serialize() for i in p]})

class export:
    def POST(self):
        '''
        Returns a string with all passwords
        ready to import
        '''
        inp = web.input()
        return backend.export(inp.cookie)

class restore:
    def POST(self):
        '''
        Restore data from a backup doit with export
        '''
        inp = web.input()
        backend.restore(inp.cookie, inp.data)


if __name__ == "__main__":
    app.run()
