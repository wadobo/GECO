#!/usr/bin/python
# -*- coding: utf-8 -*-

import web
from web import form
from utils import authenticated, templated

web.config.debug = False
#web.SERVER = 'https://danigm.net:8080/api'
web.SERVER = 'http://localhost:5000/api'

#web.DATABASE = 'sqlite:////usr/share/gecod/database.sqlite'
web.DATABASE = 'sqlite:////home/danigm/Projects/geco/src/gecod/database.sqlite'


def bootstrap_render(self):
        out = ''
        out += self.rendernote(self.note)
        out += '<div class="form">\n'

        def rendernote(note):
            if note: return '<span class="help-inline">%s</span>' % web.form.net.websafe(note)
            else: return ""

        for i in self.inputs:
            html = web.form.utils.safeunicode(i.pre) + i.render() + rendernote(i.note) + web.form.utils.safeunicode(i.post)
            if i.is_hidden():
                out += '<div style="display: none;">%s</div>\n' % (html)
            else:
                out += '<div class="control-group%s">' % (' error' if i.note else '')
                out += '<label for="%s">%s</label>' % (i.id, web.form.net.websafe(i.description))
                out += html
                out += '</div>'
        out += "</div>"
        return out

web.form.Form.render = bootstrap_render

try:
    from api import api
except:
    api = None


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
    templated = render.master(css=['style', 'bootstrap'],
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
    @templated(css='style bootstrap', title='GECO Web Client - ERROR')
    def GET(self, *args):
        render = web.template.render('templates')
        return render.error()


if __name__ == '__main__':
    app.run()
