#!/usr/bin/python

from flask import Flask
from flask.views import MethodView
from flask import jsonify
from flask import request

import json
import datetime
import backend


class CustomEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, backend.Password):
            pw = dict(type = obj.type,
                      name = obj.name,
                      description = obj.description,
                      account = obj.account,
                      password = obj.password,
                      cypher_method = obj.cypher_method,
                      updated = obj.updated,
                      expiration = obj.expiration,
                    )
            return pw
        return json.JSONEncoder.default(self, obj)



class Frontend:
    def __init__(self):
        pass

    def m_auth(self, user, password):
        ''' Return the cookie. '''
        return backend.auth(user, 'password',
                password=password)

    def m_logout(self, cookie):
        backend.logout(cookie)

    def m_register(self, user, password):
        backend.register(user, password)

    def m_unregister(self, cookie):
        backend.unregister(cookie)

    def m_change_password(self, cookie, new_password):
        backend.change_password(cookie, new_password)

    def m_change_attr(self, cookie, name, args):
        ''' args is a dict with possible keys: type, description, account, expiration, password. expiration must be an integer (days) '''
        if args.get('expiration', ''):
            args['expiration'] = datetime.datetime.now() + datetime.timedelta(int(args['expiration']))
        backend.change_attr(cookie, name, **args)

    def m_check_user_name(self, name):
        return backend.check_user_name(name)

    def m_set_password(self, cookie, name, password, args):
        ''' args is a dict with possible keys: type, description, account, expiration. expiration must be an integer (days) '''
        backend.set_password(cookie, name, password, **args)

    def m_del_password(self, cookie, name):
        backend.del_password(cookie, name)

    def m_get_password(self, cookie, name):
        p = backend.get_password(cookie, name)
        return p

    def m_get_passwords(self, cookie, args):
        ''' args is a dict with possible keys: name, type, updated, expiration, account '''
        p = backend.get_passwords_by(cookie, **args)
        return [i for i in p]

    def m_get_all_passwords(self, cookie):
        ''' Return all passwords of user '''
        p = backend.get_all_passwords(cookie)
        return [i for i in p]

    def m_export(self, cookie):
        ''' Returns a string with all passwords, ready to import '''
        return backend.export(cookie)

    def m_restore(self, cookie, data):
        ''' Restore data from a backup doit with export '''
        backend.restore(cookie, data)

    def allowed(self, method=None):
        allowed = {}
        for i in dir(self):
            if method and not i == "m_%s" % method:
                continue

            if not i.startswith("m_"):
                continue
            doc = getattr(self, i).__doc__
            doc = doc.strip() if doc else ""

            argcount = getattr(self, i).func_code.co_argcount
            params = getattr(self, i).func_code.co_varnames[1:argcount]
            allowed[i[2:]] = {'doc': doc, 'params': params, }

        return allowed


app = Flask(__name__)
app.json_encoder = CustomEncoder


class API(MethodView, Frontend):
    methods = ['GET', 'POST']

    def get(self, method=None):
        return self.view(method)

    def post(self, method=None):
        return self.view(method)

    def view(self, method):
        data = request.form.to_dict()
        args = data.get('args', None)
        if args:
            data['args'] = json.loads(args)
        f = getattr(self, "m_%s" % method, None)

        if not f:
            return jsonify(status='error',
                           msg='method not found',
                           allowed=self.allowed())

        try:
            response = f(**data)
        except TypeError:
            return jsonify(status='error',
                           msg='incorrect params',
                           allowed=self.allowed(method))
        except Exception as e:
            return jsonify(status='error', msg=e.message)

        return jsonify(status='ok', data=response)


app.add_url_rule('/<path:method>', view_func=API.as_view('api'))


if __name__ == "__main__":
    app.run()
