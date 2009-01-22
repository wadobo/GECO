#!/usr/bin/python
# -*- coding: utf-8 -*-

import web
from web import form

web.config.debug = False
web.SERVER = 'https://danigm.net:10000'

urls = (
        '/logout', 'login.logout',
        '/login', 'login.login',
        '/register', 'login.register',
        '/list', 'list.list',
        '/getpwd/(.*)', 'ajax.getpwd'
        '/(.*)', 'index',
        )

app = web.application(urls, globals())
session = web.session.Session(app, web.session.DiskStore('sessions'))

web.ses = session

class index:
    render = web.template.render('templates')
    def GET(self, args):
        username = session.get('username', '')
        if username:
            raise web.seeother('/list')
        else:
            raise web.seeother('/login')

if __name__ == '__main__':
    app.run()
