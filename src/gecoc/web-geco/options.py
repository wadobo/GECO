# -*- coding: utf-8 -*-
import web
from web import form

from utils import authenticated, templated, flash, get_gso

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
        gso = get_gso(cookie=cookie)
        web.header('Content-type','text/txt')
        return gso.export()

class options:
    render = web.template.render('templates')
    @authenticated
    @templated(css='style',
            menu=web.menu_user,
            title='GECO Web Client - Options')
    def GET(self):
        session = web.ses
        cookie = session.get('gso', '')
        gso = get_gso(cookie=cookie)
        return self.render.options(web.ses.username, web.SERVER, change_pass(),
                delete())

    @authenticated
    @templated(css='style',
            menu=web.menu_user,
            title='GECO Web Client - Options')
    def POST(self):
        session = web.ses
        cookie = session.get('gso', '')
        gso = get_gso(cookie=cookie)
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
    gso = get_gso()
    gso.auth(username, password)

    if gso.name:
        return True
    else:
        return False
