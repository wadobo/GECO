# -*- coding: utf-8 -*-
import web

from utils import authenticated, templated, flash
import gecoc.gecolib as gecolib

session = web.ses

class delete:
    render = web.template.render('templates')
    @authenticated
    def GET(self, name):
        username = session.get('username', '')
        cookie = session.get('gso', '')
        gso = gecolib.GSO(xmlrpc_server=web.SERVER, cookie=cookie)

        gso.del_password(name)
        flash("Contraseña '%s' borrada" % str(name))
        raise web.seeother('/list')

