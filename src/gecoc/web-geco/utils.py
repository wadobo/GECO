# -*- coding: utf-8 -*-
import base64
import web

def authenticated(function):
    session = web.ses
    def new_function(*args, **kwargs):
        username = session.get('username', '')
        if username:
            return function(*args, **kwargs)
        else:
            raise web.seeother('/login')

    return new_function

def error(function):
    def new_function(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except Exception, e:
            if type(e) == type(web.seeother('')):
                raise
            else:
                try:
                    flash(e.faultString, 'error')
                except:
                    flash(str(e), 'error')

                raise web.seeother('/error')

    return new_function

def templated(css='', js='', title='', menu=[]):
    css = css.split(' ') if css else []
    js = js.split(' ') if js else []
    render = web.template.render('templates')
    def new_deco(function):
        def new_function(*args, **kwargs):
            e = get_err()
            m = get_msg()

            body = function(*args, **kwargs)

            templated = render.master(title=title, css=css,
                    js=js, body=body, errors=e, msgs=m, menu=menu)
            return templated
        
        return new_function

    return new_deco


def flash(msg, t='msg'):
    '''
    t could be msg or error
    '''

    enc = base64.b64encode

    session = web.ses

    if t == 'msg':
        if type(msg) == type([]):
            session.msgs = map(enc, msg)
        else:
            session.msgs = [enc(str(msg))]
    else:
        if type(msg) == type([]):
            session.errors = map(enc, msg)
        else:
            session.errors = [enc(str(msg))]

def get_msg():
    dec = base64.b64decode

    session = web.ses
    m = session.pop('msgs', '')
    return map(dec, m)

def get_err():
    dec = base64.b64decode

    session = web.ses
    e = session.pop('errors', '')
    return map(dec, e)
