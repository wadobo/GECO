# -*- coding: utf-8 -*-

'''
Provides somes functions to interact with database withouth knowing
it. Gecod-backend provides an abstraction layer over gecod-database.
'''

# ============================================================ #
# TODO Funciones necesarias:                                   #
#                                                              #
# - Diferentes metodos de autenticación                        # 
# - consultar password por diferentes atributos (nombre)       # 
# - almacenar password                                         #
# - consultar ficheros de configuración                        # 
# - almacenar ficheros de configuración                        #
#                                                              # 
# ============================================================ #

import sys
import database as db


session = db.connect()

def __user_by_cookie(cookie):
    user = session.query(db.User).\
            filter(db.User.id == db.Cookie.user_id).\
            filter(db.Cookie.id == cookie).one()
    return user

def auth(name, method, **kwargs):
    if method == 'password':
        return auth_by_password(name, kwargs['password'])
    else:
        raise Exception('Authentication method not implemented %s' %\
                method)

def auth_by_password(name, password):
    # python 2.6 compatible
    if sys.version_info[1] == 6:
        from hashlib import sha1 as sha
    else:
        import sha
        sha = sha.new

    password_hash = sha(password).hexdigest()
    db_user = session.query(db.User).\
            filter(db.User.name == name).one()
    if db_user.password == password_hash:
        cookie = db.Cookie()
        db_user.cookie = cookie
        session.commit()
        return cookie.id
    else:
        return None

def logout(cookie):
    c = session.query(db.Cookie).filter(db.Cookie.id == cookie).one()

    session.delete(c)
    session.commit()

def get_password(cookie, name=''):
    user = __user_by_cookie(cookie)
    return session.query(db.Password)\
            .filter(db.Password.user_id == user.id)\
            .filter(db.Password.name == name).first()
