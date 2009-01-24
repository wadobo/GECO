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

def templated(css='', js='', title=''):
    css = css.split(' ') if css else []
    js = js.split(' ') if js else []
    render = web.template.render('templates')
    def new_deco(function):
        def new_function(*args, **kwargs):
            session = web.ses
            e = session.pop('errors', '')
            m = session.pop('msgs', '')

            body = function(*args, **kwargs)

            templated = render.master(title=title, css=css,
                    js=js, body=body, errors=e, msgs=m)
            return templated
        
        return new_function

    return new_deco


def flash(msg, t='msg'):
    '''
    t could be msg or error
    '''

    session = web.ses

    if t == 'msg':
        if type(msg) == type([]):
            session.msgs = msg
        else:
            session.msgs = [str(msg)]
    else:
        if type(msg) == type([]):
            session.errors = msg
        else:
            session.errors = [str(msg)]
