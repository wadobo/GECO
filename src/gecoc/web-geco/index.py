#!/usr/bin/python
# -*- coding: utf-8 -*-

import web
from web import form

urls = (
        '/logout', 'logout',
        '/login', 'login',
        '/(.*)', 'index'
        )

app = web.application(urls, globals())
session = web.session.Session(app, web.session.DiskStore('sessions'))

vname = form.regexp("\w*$", 'must be alphanumeric and _')
vpass = form.regexp(r".{3,20}", 'must be between 3 and 20 characters')

lform = form.Form(
    form.Textbox("username", vname, description="Username"),
    form.Password("password", vpass, description="Password"),
    form.Button("submit", type="submit", description="Login"),
)

render = web.template.render('templates')

class index:
    def GET(self, args):
        username = session.get('username', '')
        if username:
            return 'ok'
        else:
            raise web.seeother('/login')

class login:
    def GET(self):
        f = lform()
        return render.master(title='GECO Web Client',
                css=['style'],
                body=render.login(f))

    def POST(self):
        f = lform()
        if not f.validates():
            raise seeother('/login')

        values = web.input()
        name = values['username']
        pwd = values['password']

        session.username = name

        raise web.seeother('/index')

class logout:
    def GET(self):
        username = session.get('username', '')
        session.username = ''
        raise web.seeother('/index')

if __name__ == '__main__':
    app.run()
