# -*- coding: utf-8 -*-
import web

import gecoc.gecolib as gecolib

session = web.ses

class getpwd:
    def GET(self, pwd):
        username = session.get('username', '')
        cookie = session.get('gso', '')
        if username:
            e = session.pop('errors', '')
            m = session.pop('msgs', '')
            return "<value>ok</value>"

        else:
            raise web.seeother('/login')
