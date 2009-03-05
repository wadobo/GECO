#!/usr/bin/python
# -*- coding: utf-8 -*-

import web
from web import form
from utils import authenticated

web.config.debug = False
web.SERVER = 'https://danigm.net:10000'
#web.SERVER = 'https://localhost:4343'

urls = (
        '/logout', 'login.logout',
        '/login', 'login.login',
        '/register', 'login.register',
        '/list', 'list.list',
        '/delete/(.*)', 'delete.delete',
        '/new/?', 'new_password.new_password',
        '/edit/(.*)', 'edit.edit',
        '/getpwd/(.*)', 'ajax.getpwd',
        '/(.*)', 'index',
        )

app = web.application(urls, globals())
session = web.session.Session(app, web.session.DiskStore('sessions'))

web.ses = session

class index:
    # Cuidado, que authenticated redirige a /login
    @authenticated
    def GET(self, args):
        raise web.seeother('/list')

if __name__ == '__main__':
    app.run()
