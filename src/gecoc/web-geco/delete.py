# -*- coding: utf-8 -*-
import web

from utils import authenticated, templated, flash, get_gso

session = web.ses

class delete:
    render = web.template.render('templates')
    @authenticated
    def GET(self, name):
        # TODO preguntar
        username = session.get('username', '')
        cookie = session.get('gso', '')
        gso = get_gso(cookie=cookie)

        gso.del_password(name)
        flash("Contraseña '%s' borrada" % str(name))
        raise web.seeother('/list')

