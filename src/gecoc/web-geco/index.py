#!/usr/bin/python
# -*- coding: utf-8 -*-

import web
from web import form

web.config.debug = False

urls = (
        '/logout', 'login.logout',
        '/login', 'login.login',
        '/register', 'login.register',
        '/(.*)', 'index'
        )

app = web.application(urls, globals())
session = web.session.Session(app, web.session.DiskStore('sessions'))

web.ses = session

class index:
    render = web.template.render('templates')
    def GET(self, args):
        username = session.get('username', '')
        if username:
            e = session.get('errors', '')
            m = session.get('msgs', '')
            session.errors = ''
            session.msgs = ''

            return self.render.master(title='GECO Web Client',
                    css=['style'],
                    body=self.render.index(username=username),
                    errors=e, msgs=m)
        else:
            raise web.seeother('/login')



if __name__ == '__main__':
    app.run()
