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
from utils import authenticated, templated, flash, get_gso

session = web.ses

vname = form.regexp("\w*$", 'Debe ser Alphanumerico')
vpass = form.regexp(r".{3,20}", 'Debe estar entre 3 y 20 caracteres')

form_login = form.Form(
    form.Textbox("username", vname, description="Usuario"),
    form.Password("password", vpass, description="Contraseña"),
)

def generate_reg_form(op1, op2):
    form_reg = form.Form(
        form.Textbox("rusername", vname, description="Usuario"),
        form.Password("rpassword", vpass, description="Contraseña"),
        form.Password("password2", description="Confirmación de contraseña"),
        form.Textbox("captcha", description="captcha %s + %s = " % (op1, op2)),
        validators = [
            form.Validator("Las contraseñas no coinciden",
                lambda i: i.rpassword == i.password2),
            form.Validator("No sabes sumar? Usa la calculadora si eso...",
                lambda i: int(i.captcha) == op1 + op2),
            ])
    return form_reg

class login:
    render = web.template.render('templates')

    @templated(css='style',
            js='jquery-1.3.1.min login',
            title='GECO Web Client')
    def GET(self):
        lform = form_login()
        op1 = random.randint(1,10) 
        op2 = random.randint(1,10)
        rform = generate_reg_form(op1, op2)
        session.rform = (op1, op2)

        return self.render.login(lform, rform)

    @templated(css='style', 
            js='jquery-1.3.1.min login',
            title='GECO Web Client')
    def POST(self):
        lform = form_login()
        if not lform.validates():
            return self.render.login(form_login=lform)

        values = web.input()
        name = values['username']
        pwd = values['password']

        gso = get_gso()
        gso.auth(name, pwd)

        if gso.name:
            session.username = name
            session.gso = gso.cookie
        else:
            flash("Usuario o contraseña incorrectos", "error")
            raise web.seeother('/login')

        raise web.seeother('/index')

class logout:
    @authenticated
    def GET(self):
        username = session.get('username', '')
        session.username = ''
        cookie = session.get('gso', '')
        gso = get_gso(cookie=cookie)
        gso.logout()
        session.gso = ''
        flash("Usuario desautenticado")
        raise web.seeother('/index')

class register:
    render = web.template.render('templates')

    @templated(css='style', title='GECO Web Client')
    def POST(self):
        rform = generate_reg_form(*session.rform)
        if not rform:
            raise web.seeother('/login')

        if not rform.validates():
            return self.render.login(form_reg=rform)
        else:
            gso = get_gso()

            values = web.input()
            name = values['rusername']
            pwd = values['rpassword']

            if gso.check_user_name(name):
                errors = [u"%s no está disponible" % name]
                flash(errors, 'error')
                return self.render.login(form_reg=rform)
            else:
                gso.register(name, pwd)

            flash([u"Registrado con exito %s" % name])
            raise web.seeother("/login")
