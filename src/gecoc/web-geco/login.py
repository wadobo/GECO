#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
This controller implements:
    /login
    /logout
'''

import web
from web import form

import gecoc.gecolib as gecolib
SERVER = 'https://danigm.net:10000'

session = web.ses

vname = form.regexp("\w*$", 'Debe ser Alphanumerico')
vpass = form.regexp(r".{3,20}", 'Debe estar entre 3 y 20 caracteres')

form_login = form.Form(
    form.Textbox("username", vname, description="Usuario"),
    form.Password("password", vpass, description="Contraseña"),
)

form_reg = form.Form(
    form.Textbox("username", vname, description="Usuario"),
    form.Password("password", vpass, description="Contraseña"),
    form.Password("password2", description="Confirmación de contraseña"),
    validators = [
        form.Validator("Las contraseñas no coinciden",
            lambda i: i.password == i.password2)]
)

class login:
    render = web.template.render('templates')

    def GET(self):
        lform = form_login()
        rform = form_reg()

        e = session.get('errors', '')
        m = session.get('msgs', '')
        session.errors = ''
        session.msgs = ''

        return self.render.master(title='GECO Web Client',
                css=['style'],
                body=self.render.login(lform, rform),
                errors=e, msgs=m)

    def POST(self):
        lform = form_login()
        if not lform.validates():
            return self.render.master(title='GECO Web Client',
                    css=['style'],
                    body=self.render.login(form_login=lform))

        values = web.input()
        name = values['username']
        pwd = values['password']

        gso = gecolib.GSO(xmlrpc_server=SERVER)
        gso.auth(name, pwd)
        
        if gso.name:
            session.username = name
            session.gso = gso.cookie
        else:
            session.errors = ["Usuario o contraseña incorrectos"]
            raise web.seeother('/login')

        raise web.seeother('/index')

class logout:
    def GET(self):
        username = session.get('username', '')
        session.username = ''
        session.gso = ''
        session.msgs = ["Usuario desautenticado"]
        raise web.seeother('/index')

class register:
    render = web.template.render('templates')
    def POST(self):
        rform = form_reg()
        if not rform.validates():
            return self.render.master(title='GECO Web Client',
                    css=['style'],
                    body=self.render.login(form_reg=rform))
        else:
            gso = session.get('gso', '')
            if not gso:
                gso = gecolib.GSO(xmlrpc_server=SERVER)

            values = web.input()
            name = values['username']
            pwd = values['password']
            if gso.check_user_name(name):
                errors = [u"%s no está disponible" % name]
                return self.render.master(title='GECO Web Client',
                    css=['style'],
                    body=self.render.login(form_reg=rform),
                    errors=errors)
            else:
                gso.register(name, pwd)

            session.msgs = [u"Registrado con exito %s" % name]
            raise web.seeother("/login")
