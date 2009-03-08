# -*- coding: utf-8 -*-
import web
from web import form

from utils import authenticated, templated, flash, error_handler
import gecoc.gecolib as gecolib

vpass = form.regexp(r".{3,20}", 'Debe estar entre 3 y 20 caracteres')

change_pass = form.Form(
        form.Password("password", vpass, description="Contraseña actual"),
        form.Password("rpassword", vpass, description="Nueva contraseña"),
        form.Password("password2", description="Confirmación de contraseña"),
        validators = [
            form.Validator("Las contraseñas no coinciden",
                lambda i: i.rpassword == i.password2),
            ])

delete = form.Form(form.Password("password", vpass,
    description="Contraseña de usuario"),)

class export:
    @authenticated
    def GET(self):
        session = web.ses
        cookie = session.get('gso', '')
        gso = gecolib.GSO(xmlrpc_server=web.SERVER, cookie=cookie)
        web.header('Content-type','text/txt')
        return gso.export()

class options:
    render = web.template.render('templates')
    @authenticated
    @templated(css='style',
            title='GECO Web Client - Options')
    def GET(self):
        session = web.ses
        cookie = session.get('gso', '')
        gso = gecolib.GSO(xmlrpc_server=web.SERVER, cookie=cookie)
        return self.render.options(web.ses.username, web.SERVER, change_pass(),
                delete())

    @error_handler
    @authenticated
    @templated(css='style',
            title='GECO Web Client - Options')
    def POST(self):
        session = web.ses
        cookie = session.get('gso', '')
        gso = gecolib.GSO(xmlrpc_server=web.SERVER, cookie=cookie)
        values = web.input()

        ####### CHANGE PASSWORD #######
        if 'change' in values:
            if not change_pass.validates():
                return self.render.options(session.username, web.SERVER,
                        change_pass(), delete())
            elif not check_user_password(session.username, values['password']):
                flash("Contraseña de usuario incorrecta", "error")
                raise web.seeother('/options')
            else:
                gso.change_password(values['rpassword'])
                flash("Contraseña cambiada correctamente")
                raise web.seeother('/options')

        ####### UNREGISTER #######
        elif 'delete' in values:
            if not delete.validates():
                return self.render.options(session.username, web.SERVER,
                        change_pass(), delete())
            elif not check_user_password(session.username, values['password']):
                flash("Contraseña de usuario incorrecta", "error")
                raise web.seeother('/options')
            else:
                flash("Usuario <b>%s</b> borrado" % session.username)
                session.username = ''
                session.gso = ''
                gso.unregister()
                raise web.seeother('/login')

        ####### importar #######
        elif 'restore' in values:
            file = web.input(myfile={})
            to_import = file['myfile'].value
            filename = file['myfile'].filename
            gso.restore(to_import)
            flash("Fichero de contraseñas <b>%s</b> importado" % filename)
            raise web.seeother('/options')

        raise web.seeother('/options')

def check_user_password(username, password):
    gso = gecolib.GSO(xmlrpc_server=web.SERVER)
    gso.auth(username, password)
    
    if gso.name:
        return True
    else:
        return False
