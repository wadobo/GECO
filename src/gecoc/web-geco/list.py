# -*- coding: utf-8 -*-
import datetime
import web

import gecoc.gecolib as gecolib

session = web.ses

class list:
    render = web.template.render('templates')
    def GET(self):
        username = session.get('username', '')
        cookie = session.get('gso', '')
        gso = gecolib.GSO(xmlrpc_server=web.SERVER, cookie=cookie)
        if username:
            e = session.pop('errors', '')
            m = session.pop('msgs', '')

            pwdlist = gso.get_all_passwords()
            for pwd in pwdlist:
                exp = pwd['expiration']
                expdate = datetime.datetime.fromtimestamp(float(exp))
                pwd['expiration'] = '%02d/%02d/%04d' % (expdate.day,
                        expdate.month, expdate.year)
                pwd['days'] = (expdate - datetime.datetime.now()).days

            body = self.render.index(username=username,
                    pwdlist=pwdlist)

            return self.render.master(title='GECO Web Client',
                    css=['style'],
                    js=['aes', 'jquery-1.3.1.min', 'md5', 'sha256',
                    'gecojs'],
                    body=body,
                    errors=e, msgs=m)
        else:
            raise web.seeother('/login')
