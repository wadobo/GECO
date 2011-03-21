#!/usr/bin/python

import web
import json
import backend

urls = (
        '/auth/(.*)/(.*)', 'auth',
        '/logout/(.*)', 'logout',
        '/register/(.*)/(.*)', 'register',
        '/unregister/(.*)', 'unregister',
        '/change_password/(.*)/(.*)', 'change_password',
        '/change_attr/(.*)/(.*)/(.*)', 'change_attr',
        '/check_user_name/(.*)', 'check_user_name',
        '/set_password/(.*)/(.*)/(.*)/(.*)', 'set_password',
        '/del_password/(.*)/(.*)', 'del_password',
        '/get_password/(.*)/(.*)', 'get_password',
        '/get_passwords/(.*)', 'get_passwords',
        '/get_all_passwords/(.*)', 'get_all_passwords',
        '/export/(.*)', 'export',
        '/restore/(.*)', 'restore',
        )

app = web.application(urls, globals())


class greet:
    def GET(self, name, name2):
        return json.dumps({'message': 'Hello, ' + name + " " + name2 + '!'})


class auth:
    def GET(self, user, password):
        '''
        Return the cookie.
        '''
        cookie = backend.auth(user, 'password', password=password)
        return json.dumps({'cookie' : cookie})

class logout:
    def GET(self, cookie):
        backend.logout(cookie)
        return json.dumps({'status' : 'ok'})

class register:
    def POST(self, user, password):
        backend.register(user, password)
        return json.dumps({'status' : 'ok'})

class unregister:
    def GET(self, cookie):
        backend.unregister(cookie)
        return json.dumps({'status' : 'ok'})

class change_password:
    def GET(self, cookie, new_password):
        backend.change_password(cookie, new_password)
        return json.dumps({'status' : 'ok'})

class change_attr:
    def GET(self, cookie, name, args):
        '''
        args is a dict with possible keys:
            type, description, account, expiration, password

            expiration must be a datetime
        '''
        backend.change_attr(cookie, name, **args)
        return json.dumps({'status' : 'ok'})


class check_user_name:
    def GET(self, name):
        result = backend.check_user_name(name)
        return json.dumps({'status' : result})

class set_password:
    def GET(self, cookie, name, password, args):
        '''
        args is a dict with possible keys:
            type, description, account, expiration

            expiration must be an integer (days)
        '''

        backend.set_password(cookie, name, password, **args)

class del_password:
    def GET(self, cookie, name):
        backend.del_password(cookie, name)
        return json.dumps({'status' : 'ok'})

class get_password: 
    def GET(self, cookie, name):
        p = backend.get_password(cookie, name)
        return json.dumps({'password' : p})

class get_passwords:
    def GET(self, cookie, args):
        '''
        args is a dict with possible keys:
            name, type, updated, expiration, account
        '''

        p = backend.get_passwords_by(cookie, **args)
        return [i for i in p]

class get_all_passwords: 
    def GET(self, cookie):
        '''
        Return all passwords of user
        '''

        p = backend.get_all_passwords(cookie)
        return [i for i in p]

class export:
    def GET(self, cookie):
        '''
        Returns a string with all passwords
        ready to import
        '''

        return backend.export(cookie)

class restore:
    def GET(self, cookie, data):
        '''
        Restore data from a backup doit with export
        '''

        backend.restore(cookie, data)


if __name__ == "__main__":
    app.run()
