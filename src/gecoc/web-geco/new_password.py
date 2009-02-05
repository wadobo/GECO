# -*- coding: utf-8 -*-
import web
from web import form

from utils import authenticated, templated, flash
import gecoc.gecolib as gecolib

vname = form.regexp("\w*$", 'Debe ser Alphanumerico')
vdesc = form.regexp(r".{0,255}", 'Debe estar entre 0 y 255 caracteres')

new_form = form.Form(
    form.Textbox("name", vname, description="Nombre"),
    form.Textbox("account", vname, description="Cuenta"),
    form.Textbox("type", vname, description="Tipo", value="website"),
    form.Textarea("description", vdesc, description="Descripción"),
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

class new_password:
    render = web.template.render('templates')
    @authenticated
    @templated(css='style',
            js='aes jquery-1.3.1.min md5 sha256 gecojs',
            title='GECO Web Client - New')
    def GET(self):
        return self.render.new(new_form())
