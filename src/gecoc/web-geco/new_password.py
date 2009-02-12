# -*- coding: utf-8 -*-
import web
from web import form

from utils import authenticated, templated, flash
import gecoc.gecolib as gecolib

vname = form.regexp("\w+$", 'Debe ser Alfanumerico, más de un carácter')
vdesc = form.regexp(r".{0,255}", 'Debe estar entre 0 y 255 caracteres')
number = form.regexp("\d+$", 'Un número, son días')

new_form = form.Form(
    form.Textbox("name", vname, description="Nombre"),
    form.Textbox("account", vname, description="Cuenta"),
    form.Textbox("type", vname, description="Tipo", value="website"),
    form.Textbox("expiration", number, description="Expiración",
        value="60"),
    form.Textarea("description", vdesc, description="Descripción"),
    form.Textbox("cpassword", description="Contraseña cifrada"),
)

class new_password:
    render = web.template.render('templates')
    @authenticated
    @templated(css='style',
            js='aes jquery-1.3.1.min md5 sha256 gecojs passwordStrengthMeter masterkey new',
            title='GECO Web Client - New')
    def GET(self):
        return self.render.new(web.ses.username, new_form())

    @authenticated
    @templated(css='style',
            js='aes jquery-1.3.1.min md5 sha256 gecojs passwordStrengthMeter masterkey new',
            title='GECO Web Client - New')
    def POST(self):
        nform = new_form()
        if not nform.validates():
            return self.render.new(web.ses.username, nform)
        
        else:
            session = web.ses
            values = web.input()
            name = values['name']
            args = {}
            args['account'] = values['account']
            password = values['cpassword']
            args['description'] = values['description']
            args['type'] = values['type']
            args['expiration'] = int(values['expiration'])

            cookie = session.get('gso', '')
            gso = gecolib.GSO(xmlrpc_server=web.SERVER, cookie=cookie)
            gso.set_raw_password(name, password, args)

            flash("Contraseña '%s' añadida" % str(name))

            raise web.seeother('/')
