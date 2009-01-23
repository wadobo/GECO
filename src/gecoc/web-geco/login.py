#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
This controller implements:
    /login
    /logout
    /register
'''

import random
import web
from web import form

import gecoc.gecolib as gecolib

session = web.ses

vname = form.regexp("\w*$", 'Debe ser Alphanumerico')
vpass = form.regexp(r".{3,20}", 'Debe estar entre 3 y 20 caracteres')

form_login = form.Form(
    form.Textbox("username", vname, description="Usuario"),
    form.Password("password", vpass, description="Contraseña"),
)

def generate_reg_form(op1, op2):
    form_reg = form.Form(
        form.Textbox("username", vname, description="Usuario"),
        form.Password("password", vpass, description="Contraseña"),
        form.Password("password2", description="Confirmación de contraseña"),
        form.Textbox("captcha", description="captcha %s + %s = " % (op1, op2)),
        validators = [
            form.Validator("Las contraseñas no coinciden",
                lambda i: i.password == i.password2),
            form.Validator("No sabes sumar? Usa la calculadora si eso...",
                lambda i: int(i.captcha) == op1 + op2),
            ])
    return form_reg

class login:
    render = web.template.render('templates')

    def GET(self):
        lform = form_login()
        op1 = random.randint(1,10) 
        op2 = random.randint(1,10)
        rform = generate_reg_form(op1, op2)
        session.rform = (op1, op2)

        e = session.pop('errors', '')
        m = session.pop('msgs', '')

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

        gso = gecolib.GSO(xmlrpc_server=web.SERVER)
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
        rform = generate_reg_form(*session.rform)
        if not rform:
            raise web.seeother('/login')
        if not rform.validates():
            return self.render.master(title='GECO Web Client',
                    css=['style'],
                    body=self.render.login(form_reg=rform))
        else:
            gso = session.get('gso', '')
            if not gso:
                gso = gecolib.GSO(xmlrpc_server=web.SERVER)

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
