# -*- coding: utf-8 -*-
import datetime
import web
from web import form

from utils import authenticated, templated, flash
import gecoc.gecolib as gecolib

vname = form.regexp("\w+$", 'Debe ser Alfanumerico, más de un carácter')
vdesc = form.regexp(r".{0,255}", 'Debe estar entre 0 y 255 caracteres')
number = form.regexp("\d+$", 'Un número, son días')

def edit_form(p):
    exp = p['expiration']
    expdate = datetime.datetime.fromtimestamp(float(exp))
    p['days'] = (expdate - datetime.datetime.now()).days

    new_form = form.Form(
        form.Textbox("name", description="Nombre", disabled="disabled", value=p['name']),
        form.Textbox("account", description="Cuenta", value=p['account']),
        form.Textbox("type", vname, description="Tipo", value=p['type']),
        form.Textbox("expiration", number, description="Expiración", value=p['days']),
        form.Textarea("description", vdesc, description="Descripción", value=p['description']),
        form.Textbox("cpassword", description="Contraseña cifrada", value=p['password']),
    )
    return new_form

class edit:
    render = web.template.render('templates')
    @authenticated
    @templated(css='style',
            js='aes jquery-1.3.1.min md5 sha256 gecojs passwordStrengthMeter masterkey new',
            menu=web.menu_user,
            title='GECO Web Client - New')
    def GET(self, name):
        session = web.ses
        cookie = session.get('gso', '')
        gso = gecolib.GSO(xmlrpc_server=web.SERVER, cookie=cookie)
        password = gso.get_password(name)
        myedit_form = edit_form(password)
        return self.render.new(web.ses.username, myedit_form(),
                title="Editar Contraseña")
    
    @authenticated
    @templated(css='style',
            js='aes jquery-1.3.1.min md5 sha256 gecojs passwordStrengthMeter masterkey new',
            menu=web.menu_user,
            title='GECO Web Client - New')
    def POST(self, name):
        session = web.ses
        cookie = session.get('gso', '')
        gso = gecolib.GSO(xmlrpc_server=web.SERVER, cookie=cookie)
        password = gso.get_password(name)
        myedit_form = edit_form(password)
        if not myedit_form.validates():
            return self.render.new(web.ses.username, myedit_form())
        
        else:
            session = web.ses
            values = web.input()
            args = {}
            args['account'] = values['account']
            password = values['cpassword']
            args['description'] = values['description']
            args['type'] = values['type']
            args['expiration'] = int(values['expiration'])

            cookie = session.get('gso', '')
            try:
                gso = gecolib.GSO(xmlrpc_server=web.SERVER, cookie=cookie)
                gso.del_password(name)
                gso.set_raw_password(name, password, args)
                flash("Contraseña <strong>'%s'</strong> modificada" % str(name))
            except:
                flash("Contraseña '%s' <strong>NO</strong> modificada" % str(name), 'error')

            raise web.seeother('/')
