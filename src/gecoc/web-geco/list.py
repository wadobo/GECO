# -*- coding: utf-8 -*-
import datetime
import web

from utils import authenticated, templated, flash
import gecoc.gecolib as gecolib

session = web.ses

class list:
    render = web.template.render('templates')
    @authenticated
    @templated(css='style',
            js='aes jquery-1.3.1.min md5 sha256 gecojs masterkey list',
            title='GECO Web Client')
    def GET(self):
        username = session.get('username', '')
        cookie = session.get('gso', '')
        gso = gecolib.GSO(xmlrpc_server=web.SERVER, cookie=cookie)

        pwdlist = gso.get_all_passwords()
        def cmp(x, y):
            if x['name'] > y['name']: return 1
            else: return -1
        pwdlist.sort(cmp)
        # Cambiando el formato de la fecha
        for pwd in pwdlist:
            exp = pwd['expiration']
            expdate = datetime.datetime.fromtimestamp(float(exp))
            pwd['expiration'] = '%02d/%02d/%04d' % (expdate.day,
                    expdate.month, expdate.year)
            pwd['days'] = (expdate - datetime.datetime.now()).days

        body = self.render.index(username=username,
                pwdlist=pwdlist)

        return body
