#!/usr/bin/python
# -*- coding: utf-8 -*-

import web
from web import form
from utils import authenticated, templated

try:
    from api import api
except:
    api = None

web.config.debug = False
#web.SERVER = 'https://danigm.net:8080'
web.SERVER = 'https://localhost:4343'

web.menu_user = (
        ('Listado', '/list'),
        ('Añadir', '/new'),
        ('Opciones', '/options'),
        )

urls = [
        '/error', 'error',
        '/logout', 'login.logout',
        '/options', 'options.options',
        '/export', 'options.export',
        '/login', 'login.login',
        '/register', 'login.register',
        '/list', 'list.list',
        '/delete/(.*)', 'delete.delete',
        '/new/?', 'new_password.new_password',
        '/edit/(.*)', 'edit.edit',
        '/getpwd/(.*)', 'ajax.getpwd',
        '/(.*)', 'index',
        ]

if api:
    urls = ['/api/(.*)', 'api'] + urls

app = web.application(urls, globals())
session = web.session.Session(app, web.session.DiskStore('sessions'))

def internalerror():
    render = web.template.render('templates')
    body = render.error()
    templated = render.master(css=['style'],
            title='GECO Web Client - ERROR',
            body=body, menu=(('Salir', '/logout'),))
    return web.internalerror(templated)

app.internalerror = internalerror

web.ses = session

class index:
    # Cuidado, que authenticated redirige a /login
    @authenticated
    def GET(self, args):
        raise web.seeother('/list')

class error:
    @templated(css='style', title='GECO Web Client - ERROR')
    def GET(self, *args):
        render = web.template.render('templates')
        return render.error()


if __name__ == '__main__':
    app.run()
